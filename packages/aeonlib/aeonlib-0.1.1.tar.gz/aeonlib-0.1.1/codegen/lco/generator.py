#!/usr/bin/env python3
import fileinput
import json
import sys
from pathlib import Path
from typing import Any

import textcase
from jinja2 import Environment, FileSystemLoader

VALID_FACILITIES = ["SOAR", "LCO", "SAAO", "BLANCO"]


def get_modes(ins: dict[str, Any], type: str) -> list[str]:
    try:
        return [m["code"] for m in ins["modes"][type]["modes"]]
    except Exception:
        return []


def generate_instrument_configs(ins_s: str, facility: str) -> str:
    """
    Generate instrument models based on the output of the OCS
    instrument data endpoint. For LCO, this endpoint resides
    at https://observe.lco.global/api/instruments/

    Args:
        ins_s (str): The input json containing instrument data.
        facility (str): Which facility to generate instruments for.

    Returns:
        str: Generated Python Pydantic models as a string.
    """

    j_env = Environment(
        loader=FileSystemLoader(Path(__file__).parent / "templates"),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = j_env.get_template("instruments.jinja")
    ins_data = json.loads(ins_s)
    instruments: list[dict[str, Any]] = []
    if facility == "SOAR":
        # Soar instruments look like SoarGhtsBluecam, already prefixed, so no need to add a prefix.
        prefix = ""
        filtered = {k: v for k, v in ins_data.items() if "soar" in k.lower()}
    elif facility == "BLANCO":
        # Blanco instrument(s) look like BLANCO_NEWFIRM
        prefix = ""
        filtered = {k: v for k, v in ins_data.items() if "blanco" in k.lower()}
    elif facility == "LCO":
        # We add a prefix for LCO because some instruments start with a number,
        # which is not allowed in Python class names. For example: Lco0M4ScicamQhy600
        prefix = "Lco"
        filtered = {
            k: v
            for k, v in ins_data.items()
            if "soar" not in k.lower() and "blanco" not in k.lower()
        }
    elif facility == "SAAO":
        # SAAO config doesn't share any instruments with other facilities so we don't need
        # to filter it
        prefix = "SAAO"
        filtered = ins_data
    else:
        raise ValueError(f"Invalid facility. Must be one of {VALID_FACILITIES}")

    # Instruments endpoint seems inconsistent, this should keep our output consistent
    ordered = dict(sorted(filtered.items()))
    for instrument_type, ins in ordered.items():
        instruments.append(
            {
                "instrument_type": instrument_type,
                "class_name": f"{prefix}{textcase.pascal(instrument_type)}",
                "config_types": [
                    c["code"] for c in ins["configuration_types"].values()
                ],
                "readout_modes": get_modes(ins, "readout"),
                "acquisition_modes": get_modes(ins, "acquisition"),
                "guiding_modes": get_modes(ins, "guiding"),
                "rotator_modes": get_modes(ins, "rotator"),
                "optical_elements": {
                    # This gets rid of the silly trailing s on "filters" and "narrowband_g_positions"
                    k.rstrip("s"): v
                    for k, v in ins["optical_elements"].items()
                },
            }
        )

    return template.render(instruments=instruments, facility=facility)


if __name__ == "__main__":
    try:
        facility = sys.argv.pop(1)
        # Accepts input from stdin or a file argument
        with fileinput.input() as f:
            ins_json = "".join(list(f))
            _ = sys.stdout.write(
                generate_instrument_configs(ins_json, facility=facility)
            )
    except IndexError:
        _ = sys.stdout.write("Usage: python generator.py <facility>")
        exit(1)
