#!/usr/bin/env python3

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

from cmk.server_side_calls.v1 import SpecialAgentConfig, SpecialAgentCommand, noop_parser

def _agent_arguments(params, _host_config):
    return [
        SpecialAgentCommand(
            command_arguments=[
                params["host"],
                params["user"],
                params["password"].unsafe(),
            ]
        )
    ]

special_agent_fc_ntp_mini = SpecialAgentConfig(
    name="fc_ntp_mini",
    parameter_parser=noop_parser,
    commands_function=_agent_arguments,
)

