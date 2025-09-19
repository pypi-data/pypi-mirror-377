# pyright: reportPrivateUsage=false
import time
from logging import getLogger

from astropy.coordinates import Angle
from lxml import etree
from suds.client import Client

from aeonlib.conf import settings
from aeonlib.lt.models import LT_INSTRUMENTS, LTConfig
from aeonlib.models import SiderealTarget, Window

LT_XML_NS = "http://www.rtml.org/v3.1a"
LT_XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
LT_SCHEMA_LOCATION = (
    "http://www.rtml.org/v3.1a http://telescope.livjm.ac.uk/rtml/RTML-nightly.xsd"
)

logger = getLogger(__name__)


class LTException(Exception):
    pass


class LTFacility:
    def __init__(self):
        headers = {
            "Username": settings.lt_username,
            "Password": settings.lt_password,
        }
        url = "{0}://{1}:{2}/node_agent2/node_agent?wsdl".format(
            "http", settings.lt_host, settings.lt_port
        )
        self.client: Client = Client(url, headers=headers)

    def submit_observation(
        self, cfg: LTConfig, ins: LT_INSTRUMENTS, target: SiderealTarget, window: Window
    ) -> str:
        observation_payload = self._observation_payload(cfg, ins, target, window)
        return self._send_payload(observation_payload)

    def validate_observation(
        self, cfg: LTConfig, ins: LT_INSTRUMENTS, target: SiderealTarget, window: Window
    ) -> str:
        observation_payload = self._observation_payload(cfg, ins, target, window)
        # Change the payload to an inquiry mode document to test connectivity
        observation_payload.set("mode", "inquiry")

        return self._send_payload(observation_payload)

    def cancel_observation(self, uid: str, project_id: str) -> str:
        cancel_payload = self._prolog(mode="abort", uid=uid)
        project = self._build_project(project_id)
        cancel_payload.append(project)

        return self._send_payload(cancel_payload)

    def _observation_payload(
        self,
        cfg: LTConfig,
        instrument: LT_INSTRUMENTS,
        target: SiderealTarget,
        window: Window,
    ) -> etree._Element:
        uid = "aeon_" + format(int(time.time()))
        payload = self._prolog(mode="request", uid=uid)
        project = self._build_project(cfg.project)
        payload.append(project)
        schedules = instrument.build_inst_schedule()
        for schedule in schedules:
            schedule.append(self._build_target(target))
            for const in self._build_constraints(cfg, window):
                schedule.append(const)
            payload.append(schedule)

        return payload

    def _send_payload(self, payload: etree._Element) -> str:
        str_payload = etree.tostring(payload, encoding="unicode", pretty_print=True)
        try:
            response = self.client.service.handle_rtml(str_payload).replace(
                'encoding="ISO-8859-1"', ""
            )
        except Exception as e:
            logger.debug("RTML submission failed with payload: %s", str_payload)
            raise LTException(f"Failed to submit observation to LT: {e}") from e

        response_rtml = etree.fromstring(response)
        mode = response_rtml.get("mode")

        if mode in ["offer", "confirm"]:
            return response_rtml.get("uid", "")
        elif mode == "reject":
            logger.debug("RTML submission rejected: %s", response)
            raise LTException("LT rejected the observation request")
        else:
            logger.debug("Unexpected RTML mode '%s' in response: %s", mode, response)
            raise LTException(
                f"Unexpected response mode from Liverpool Telescope: {mode}"
            )

    def _prolog(self, mode: str, uid: str) -> etree._Element:
        namespaces = {"xsi": LT_XSI_NS}
        schemaLocation = str(etree.QName(LT_XSI_NS, "schemaLocation"))

        return etree.Element(
            "RTML",
            {schemaLocation: LT_SCHEMA_LOCATION},
            xmlns=LT_XML_NS,
            mode=mode,
            uid=uid,
            version="3.1a",
            nsmap=namespaces,
        )

    def _build_project(self, project_id: str) -> etree._Element:
        project = etree.Element("Project", ProjectID=project_id)
        contact = etree.SubElement(project, "Contact")
        etree.SubElement(contact, "Username").text = settings.lt_username
        etree.SubElement(contact, "Name").text = ""
        _ = etree.SubElement(contact, "Communication")

        return project

    def _build_target(self, aeon_target: SiderealTarget) -> etree._Element:
        target = etree.Element("Target", name=aeon_target.name)
        coordinates = etree.SubElement(target, "Coordinates")
        etree.SubElement(coordinates, "Equinox").text = str(aeon_target.epoch)

        ra = etree.SubElement(coordinates, "RightAscension")
        assert isinstance(aeon_target.ra, Angle)
        etree.SubElement(ra, "Hours").text = str(int(aeon_target.ra.hms.h))
        etree.SubElement(ra, "Minutes").text = str(int(aeon_target.ra.hms.m))
        etree.SubElement(ra, "Seconds").text = str(aeon_target.ra.hms.s)

        dec = etree.SubElement(coordinates, "Declination")
        assert isinstance(aeon_target.dec, Angle)
        sign = "+" if aeon_target.dec.signed_dms.sign == 1.0 else "-"
        etree.SubElement(dec, "Degrees").text = sign + str(
            int(aeon_target.dec.signed_dms.d)
        )
        etree.SubElement(dec, "Arcminutes").text = str(
            int(aeon_target.dec.signed_dms.m)
        )
        etree.SubElement(dec, "Arcseconds").text = str(aeon_target.dec.signed_dms.s)

        return target

    def _build_constraints(
        self, lt_observation: LTConfig, window: Window
    ) -> list[etree._Element]:
        airmass_const = etree.Element(
            "AirmassConstraint", maximum=str(lt_observation.max_airmass)
        )

        sky_const = etree.Element("SkyConstraint")
        etree.SubElement(sky_const, "Flux").text = str(lt_observation.max_skybrightness)
        etree.SubElement(sky_const, "Units").text = "magnitudes/square-arcsecond"

        seeing_const = etree.Element(
            "SeeingConstraint",
            maximum=str(lt_observation.max_seeing),
            units="arcseconds",
        )

        photom_const = etree.Element("ExtinctionConstraint")
        etree.SubElement(photom_const, "Clouds").text = lt_observation.photometric
        date_const = etree.Element("DateTimeConstraint", type="include")
        assert window.start
        start = window.start.strftime("%Y-%m-%dT%H:%M:00+00:00")  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        end = window.end.strftime("%Y-%m-%dT%H:%M:00+00:00")  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        _ = etree.SubElement(date_const, "DateTimeStart", system="UT", value=str(start))  # pyright: ignore[reportUnknownArgumentType]
        _ = etree.SubElement(date_const, "DateTimeEnd", system="UT", value=str(end))  # pyright: ignore[reportUnknownArgumentType]

        return [airmass_const, sky_const, seeing_const, photom_const, date_const]
