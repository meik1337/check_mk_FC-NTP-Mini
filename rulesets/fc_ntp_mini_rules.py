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

from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Float,
    LevelDirection,
    SimpleLevels,
    Integer,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, Topic, HostCondition


def _parameter_form_fc_ntp_mini():
    return Dictionary(
        elements={
            "levels_gpsinfo": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Levels for GPS Satellites"),
                    form_spec_template=Integer(),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=DefaultValue(value=(5, 3)),
                ),
                required=False,
            ),
            "levels_bdinfo": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Levels for BeiDou Satellites"),
                    form_spec_template=Integer(),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=DefaultValue(value=(5, 3)),
                ),
                required=False,
            ),
            "levels_glinfo": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Levels for GLONASS Satellites"),
                    form_spec_template=Integer(),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=DefaultValue(value=(5, 3)),
                ),
                required=False,
            ),
        }
    )

rule_spec_fc_ntp_mini = CheckParameters(
    name="fc_ntp_mini",
    title=Title("fc_ntp_mini Check parameters"),
    topic=Topic.APPLICATIONS,
    parameter_form=_parameter_form_fc_ntp_mini,
    condition=HostCondition(),
)
