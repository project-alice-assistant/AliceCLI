#  Copyright (c) 2021
#
#  This file, AliceCli.py, is part of Project Alice CLI.
#
#  Project Alice CLI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>
#
#  Last modified: 2021.03.04 at 15:56:11 CET
#  Last modified by: Psycho

import click

from . import MainMenu
from .alice import alice
from .install import install
from .utils import commons, utils


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context):
	if ctx.invoked_subcommand is None:
		click.clear()
		ctx.invoke(MainMenu.mainMenu)


cli.add_command(MainMenu.mainMenu)
cli.add_command(commons.connect)
cli.add_command(commons.discover)
cli.add_command(utils.reboot)
cli.add_command(utils.updateSystem)
cli.add_command(utils.upgradeSystem)
cli.add_command(utils.soundTest)
cli.add_command(utils.aliceLogs)
cli.add_command(utils.systemLogs)
cli.add_command(utils.changeHostname)
cli.add_command(utils.changePassword)
cli.add_command(alice.updateAlice)
cli.add_command(alice.systemctl)
cli.add_command(alice.reportBug)
cli.add_command(install.installAlice)
cli.add_command(install.installSoundDevice)
cli.add_command(install.uninstallSoundDevice)
cli.add_command(install.prepareSdCard)
