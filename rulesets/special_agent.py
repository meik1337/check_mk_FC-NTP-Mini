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


from cmk.rulesets.v1.form_specs import Dictionary, DictElement, Password, migrate_to_password, String
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic, Title, Help

def _formspec():
    return Dictionary(
        title=Title("FC-NTP-MINI Appliance"),
        help_text=Help("Configuration for accessing the Webinterface of FC-NTP-MINI via Special Agent."),
        elements={
            "host": DictElement(
                required=True,
                parameter_form=String(title=Title("Device Hostname or IP Address"))
            ),
            "user": DictElement(
                required=True,
                parameter_form=String(title=Title("HTTP Username"))
            ),
            "password": DictElement(
                required=True,
                parameter_form=Password(title=Title("HTTP Password"), migrate=migrate_to_password)
            ),
        }
    )

rule_spec_fc_ntp_mini = SpecialAgent(
    name="fc_ntp_mini",
    topic=Topic.NETWORKING,
    title=Title("FC-NTP-MINI Appliance"),
    parameter_form=_formspec,
)
