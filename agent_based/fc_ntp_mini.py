#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# +------------------------------------------------------------+
# |                                                            |
# |             | |             | |            | |             |
# |          ___| |__   ___  ___| | ___ __ ___ | | __          |
# |         / __| '_ \ / _ \/ __| |/ / '_ ` _ \| |/ /          |
# |        | (__| | | |  __/ (__|   <| | | | | |   <           |
# |         \___|_| |_|\___|\___|_|\_\_| |_| |_|_|\_\          |
# |                                 custom code by Meik Vogel  |
# |                                                            |
# +------------------------------------------------------------+
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   Copyright (C) 2025  uvitas eGbR
#                       by meik.vogel@uvitas.de

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    Service,
    Result,
    State,
    Metric,
)
import re

DISPLAY_NAMES = {
    "current_time_utc": "NTP Current UTC Time",
    "ant": "GNSS Antenna",
    "const": "GNSS Constellations",
    "svused": "GNSS Satellites",
    "gpsinfo": "GNSS GPS Satellites",
    "bdinfo": "GNSS BeiDou Satellites",
    "glinfo": "GNSS GLONASS Satellites",
    "latlongalt": "GNSS Position",
    "ntp_server_status": "NTP Server",
    "ntp_port": "NTP Server Port",
    "ntp_stratum": "NTP Stratum",
}

def parse_fc_ntp_mini(string_table):
    parsed = {}
    for line in string_table:
        if not line:
            continue
        key = line[0].rstrip(":")
        value = " ".join(line[1:]) if len(line) > 1 else ""
        parsed[key] = value
    return parsed

def discover_fc_ntp_mini(section):
    for key in DISPLAY_NAMES:
        if key == "latlongalt":
            if all(k in section for k in ["lat", "long", "alt"]):
                yield Service(item=DISPLAY_NAMES[key])
        elif key in section:
            yield Service(item=DISPLAY_NAMES[key])

def convert_gdm_to_dd(coord_str):
    match = re.match(r"([NSWE])\s*(\d+)(\d\d\.\d+)", coord_str)
    if not match:
        return None
    direction, degrees, minutes = match.groups()
    degrees = int(degrees)
    minutes = float(minutes)
    decimal = degrees + minutes / 60
    if direction in ["S", "W"]:
        decimal *= -1
    return round(decimal, 6)

def check_fc_ntp_mini(item, params, section):
    reverse_map = {v: k for k, v in DISPLAY_NAMES.items()}
    internal_key = reverse_map.get(item)

    if internal_key == "latlongalt":
        lat_raw = section.get("lat", "")
        lon_raw = section.get("long", "")
        alt = section.get("alt", "")
        lat_dd = convert_gdm_to_dd(lat_raw)
        lon_dd = convert_gdm_to_dd(lon_raw)

        if lat_dd is not None and lon_dd is not None and alt:
            google_link = f"https://maps.google.com/?q={lat_dd},{lon_dd}"
            summary = f"{lat_dd}, {lon_dd}, Altitude: {alt} → {google_link}"
            yield Result(state=State.OK, summary=summary)
        else:
            yield Result(state=State.UNKNOWN, summary="Coordinates incomplete or invalid")
        return

    value = section.get(internal_key)
    if value is None or value.strip() == "":
        yield Result(state=State.UNKNOWN, summary="No value found")
        return

    if internal_key == "ant":
        state = State.OK if value.strip().lower() == "ok" else State.CRIT
        yield Result(state=state, summary=f"Status: {value}")
        return

    if internal_key == "ntp_server_status":
        state = State.OK if value.strip().lower() == "active" else State.CRIT
        yield Result(state=state, summary=f"Status: {value}")
        return

    if internal_key == "ntp_stratum":
        try:
            val = int(value)
            state = State.OK if val <= 2 else State.WARN
            yield Result(state=state, summary=f"Stratum: {val}")
        except ValueError:
            yield Result(state=State.UNKNOWN, summary="Stratum: Invalid format")
        return

    if internal_key == "ntp_port":
        try:
            port = int(value)
            yield Result(state=State.OK, summary=f"Port: {port}")
        except ValueError:
            yield Result(state=State.OK, summary=f"Port: {value}")
        return

    if internal_key == "svused":
        try:
            count = int(value)
            state = State.OK if count >= 5 else State.WARN
            yield Result(state=state, summary=f"{count} satellites in use")
            yield Metric(name="svused_used", value=count)
        except ValueError:
            yield Result(state=State.UNKNOWN, summary="Invalid satellite count")
        return

    if internal_key in ["gpsinfo", "bdinfo", "glinfo"]:
        match = re.match(r"(\d+)/(\d+)", value)
        if match:
            used, visible = map(int, match.groups())

            thresholds = (5, 3)

            if hasattr(params, 'get'):
                level_tuple = params.get(f"levels_{internal_key}")

                if level_tuple and hasattr(level_tuple, "__getitem__") and len(level_tuple) == 2:
                    level_type, levels = level_tuple

                    if level_type == "no_levels":
                        yield Result(state=State.OK, summary="No levels configured - always OK")
                        yield Metric(name=f"{internal_key}_used", value=used)
                        yield Metric(name=f"{internal_key}_visible", value=visible)
                        return
                    elif levels is not None:
                        thresholds = levels

            warn, crit = thresholds

            if used < crit:
                state = State.CRIT
            elif used < warn:
                state = State.WARN
            else:
                state = State.OK

            summary = f"{used} used (warn < {warn}, crit < {crit}) / {visible} visible"
            yield Result(state=state, summary=summary)
            yield Metric(name=f"{internal_key}_used", value=used)
            yield Metric(name=f"{internal_key}_visible", value=visible)
        else:
            yield Result(state=State.UNKNOWN, summary="Invalid format")
        return


    yield Result(state=State.OK, summary=f"{value}")


agent_section_fc_ntp_mini = AgentSection(
    name="fc_ntp_mini",
    parse_function=parse_fc_ntp_mini,
)

check_plugin_fc_ntp_mini = CheckPlugin(
    name="fc_ntp_mini",
    service_name="%s",
    discovery_function=discover_fc_ntp_mini,
    check_function=check_fc_ntp_mini,
    check_default_parameters={
        "levels_gpsinfo": ("fixed", (5, 3)),
        "levels_bdinfo": ("fixed", (5, 3)),
        "levels_glinfo": ("fixed", (5, 3)),
    },
    check_ruleset_name="fc_ntp_mini",
)
