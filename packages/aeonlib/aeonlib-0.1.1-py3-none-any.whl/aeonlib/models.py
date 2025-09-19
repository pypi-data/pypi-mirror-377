"""
Models shared between facilities.
"""

from typing import Annotated, Any, ClassVar, Literal

from annotated_types import Le
from pydantic import BaseModel, ConfigDict
from pydantic.types import (
    NonNegativeFloat,
    StringConstraints,
)

from aeonlib.types import Angle, Time, TimeMJD


class SiderealTarget(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(validate_assignment=True)
    name: Annotated[str, StringConstraints(max_length=50)] = "string"
    """The name of this Target"""
    type: Literal["ICRS", "HOUR_ANGLE", "ALTAZ"]
    """The type of this Target"""
    hour_angle: Angle | None = None
    """Hour angle of this Target in decimal degrees"""
    ra: Angle
    """Right ascension in decimal degrees"""
    dec: Angle
    """Declination in decimal degrees"""
    altitude: Angle | None = None
    """Altitude of this Target in decimal degrees"""
    azimuth: Angle | None = None
    """Azimuth of this Target in decimal degrees east of North"""
    proper_motion_ra: Annotated[float, Le(20000.0)] = 0
    """Right ascension proper motion of the Target in mas/year. Defaults to 0."""
    proper_motion_dec: Annotated[float, Le(20000.0)] = 0
    """Declination proper motion of the Target in mas/year. Defaults to 0."""
    epoch: Annotated[int, Le(2100)] = 2000
    """Epoch of coordinates in Julian Years. Defaults to 2000."""
    parallax: Annotated[float, Le(2000)] = 0
    """Parallax of the Target in mas, max 2000. Defaults to 0."""


class Window(BaseModel):
    """A general time window"""

    model_config: ClassVar[ConfigDict] = ConfigDict(validate_assignment=True)
    start: Time | None = None
    end: Time


class _NonSiderealTarget(BaseModel):
    """Base class for non-sidereal targets, should not be used directly"""

    model_config: ClassVar[ConfigDict] = ConfigDict(validate_assignment=True)
    type: Literal["ORBITAL_ELEMENTS"] = "ORBITAL_ELEMENTS"
    name: Annotated[str, StringConstraints(max_length=50)]
    epochofel: TimeMJD
    """The epoch of the orbital elements (MJD)"""
    orbinc: Angle
    """Orbital inclination"""
    longascnode: Angle
    """Longitude of ascending node"""
    eccentricity: NonNegativeFloat
    """Eccentricity of the orbit"""
    extra_params: dict[Any, Any] = {}


class AsaMajorPlanetTarget(_NonSiderealTarget):
    scheme: Literal["ASA_MAJOR_PLANET"] = "ASA_MAJOR_PLANET"
    longofperih: Angle
    """Longitude of perihelion"""
    meandist: Annotated[float, NonNegativeFloat]
    """Semi-major axis (AU)"""
    meanlong: Angle
    """Mean longitude"""
    dailymot: Angle
    """Mean Daily motion"""


class AsaMinorPlanetTarget(_NonSiderealTarget):
    scheme: Literal["ASA_MINOR_PLANET"] = "ASA_MINOR_PLANET"
    argofperih: Angle
    """Argument of perihelion"""
    meandist: Annotated[float, NonNegativeFloat]
    """Semi-major axis (AU)"""
    meananom: Angle
    """Mean anomaly"""


class AsaCometTarget(_NonSiderealTarget):
    scheme: Literal["ASA_COMET"] = "ASA_COMET"
    argofperih: Angle
    """Argument of perihelion"""
    perihdist: Annotated[float, NonNegativeFloat]
    """Perihelion distance (AU)"""
    epochofperih: TimeMJD
    """Epoch of perihelion (MJD)"""


class JplMajorPlanetTarget(_NonSiderealTarget):
    scheme: Literal["JPL_MAJOR_PLANET"] = "JPL_MAJOR_PLANET"
    argofperih: Angle
    """Argument of perihelion"""
    meandist: Annotated[float, NonNegativeFloat]
    """Semi-major axis (AU)"""
    meananom: Angle
    """Mean anomaly"""
    dailymot: Angle
    """Mean Daily motion"""


class JplMinorPlanetTarget(_NonSiderealTarget):
    scheme: Literal["JPL_MINOR_PLANET"] = "JPL_MINOR_PLANET"
    argofperih: Angle
    """Argument of perihelion"""
    perihdist: Annotated[float, NonNegativeFloat]
    """Perihelion distance (AU)"""
    epochofperih: TimeMJD
    """Epoch of perihelion (MJD)"""


class MpcMinorPlanetTarget(_NonSiderealTarget):
    scheme: Literal["MPC_MINOR_PLANET"] = "MPC_MINOR_PLANET"
    argofperih: Angle
    """Argument of perihelion"""
    meandist: Annotated[float, NonNegativeFloat]
    """Semi-major axis (AU)"""
    meananom: Angle
    """Mean anomaly"""


class MpcCometTarget(_NonSiderealTarget):
    scheme: Literal["MPC_COMET"] = "MPC_COMET"
    argofperih: Angle
    """Argument of perihelion"""
    perihdist: Annotated[float, NonNegativeFloat]
    """Perihelion distance (AU)"""
    epochofperih: TimeMJD
    """Epoch of perihelion (MJD)"""


class GeocentricSatelliteTarget(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(validate_assignment=True)
    name: Annotated[str, StringConstraints(max_length=50)]
    type: Literal["SATELLITE"] = "SATELLITE"
    altitude: Angle
    """Altitude of this Target in decimal degrees"""
    azimuth: Angle
    """Azimuth of this Target in decimal degrees east of North"""
    diff_altitude_rate: float
    """Differential altitude rate (arcsec/s)"""
    diff_azimuth_rate: float
    """Differential azimuth rate (arcsec/s)"""
    diff_epoch: float
    """Reference time for non-sidereal motion (MJD)"""
    diff_altitude_acceleration: float
    """Differential altitude acceleration (arcsec/s^2)"""
    diff_azimuth_acceleration: float
    """Differential azimuth acceleration (arcsec/s^2)"""
    extra_params: dict[Any, Any] = {}


TARGET_TYPES = (
    SiderealTarget
    | AsaMajorPlanetTarget
    | AsaMinorPlanetTarget
    | AsaCometTarget
    | JplMajorPlanetTarget
    | JplMinorPlanetTarget
    | MpcMinorPlanetTarget
    | MpcCometTarget
    | GeocentricSatelliteTarget
)
