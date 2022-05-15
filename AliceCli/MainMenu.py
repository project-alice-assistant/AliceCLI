#  Copyright (c) 2021
#
#  This file, MainMenu.py, is part of Project Alice CLI.
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
#  Last modified: 2021.03.07 at 10:56:35 CET
#  Last modified by: Psycho
import click
import re
import subprocess
import sys
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from AliceCli.Version import Version
from AliceCli.alice.alice import reportBug, systemctl, updateAlice
from AliceCli.install.install import installAlice, installAliceSatellite, installSoundDevice, prepareSdCard, uninstallSoundDevice
from AliceCli.utils.commons import connect, discover
from AliceCli.utils.utils import aliceLogs, changeHostname, changePassword, disableRespeakerLeds, reboot, soundTest, systemLogs, updateSystem, upgradeSystem


VERSION = ''
CHECKED = False

@click.command(name='main_menu')
@click.pass_context
def mainMenu(ctx: click.Context):
	global CHECKED, VERSION

	click.clear()

	if not CHECKED:
		result = subprocess.run('pip index versions projectalice-cli'.split(), capture_output=True, text=True)
		if 'error' not in result.stderr.lower():
			regex = re.compile(r"INSTALLED:.*(?P<installed>[\d]+\.[\d]+\.[\d]+)\n.*LATEST:.*(?P<latest>[\d]+\.[\d]+\.[\d]+)")
			match = regex.search(result.stdout.strip())

			if not match:
				click.secho(message='Failed checking CLI version\n', fg='red')
			else:
				installed = Version.fromString(match.group('installed'))
				latest = Version.fromString(match.group('latest'))

				if installed < latest:
					click.secho(f'Project Alice CLI version {str(installed)}\n', fg='red')
					click.secho(message=f'CLI version {str(latest)} is available, you should consider updating using `pip install projectalice-cli --upgrade`\n', fg='red')
				else:
					click.secho(f'Project Alice CLI version {str(installed)}\n', fg='green')

				VERSION = str(installed)
		else:
			click.secho(message='Failed checking CLI version\n', fg='red')

		CHECKED = True
	else:
		click.echo(f'Project Alice CLI version {VERSION}\n')

	action = inquirer.select(
		message='',
		default=None,
	    choices=[
		    Separator(line='\n------- Network -------'),
			Choice(lambda: ctx.invoke(discover), name='Discover devices on network'),
			Choice(lambda: ctx.invoke(connect), name='Connect to a device'),
		    Separator(line='\n------- Setup -------'),
			Choice(lambda: ctx.invoke(prepareSdCard), name='Prepare your SD card'),
			Choice(lambda: ctx.invoke(changePassword), name='Change device\'s password'),
			Choice(lambda: ctx.invoke(changeHostname), name='Set device\'s name'),
			Choice(lambda: ctx.invoke(installSoundDevice), name='Install your sound device'),
			Choice(lambda: ctx.invoke(soundTest), name='Sound test'),
			Choice(lambda: ctx.invoke(installAlice), name='Install Alice'),
			Choice(lambda: ctx.invoke(installAliceSatellite), name='Install Alice Satellite'),
		    Separator(line='\n------- Service -------'),
			Choice(lambda: ctx.invoke(systemctl, option='start'), name='Start Alice'),
		    Choice(lambda: ctx.invoke(systemctl, option='restart'), name='Restart Alice'),
		    Choice(lambda: ctx.invoke(systemctl, option='stop'), name='Stop Alice'),
		    Choice(lambda: ctx.invoke(systemctl, option='enable'), name='Enable Alice service'),
		    Choice(lambda: ctx.invoke(systemctl, option='disable'), name='Disable Alice service'),
		    Separator(line='\n------- Updates -------'),
		    Choice(lambda: ctx.invoke(updateAlice), name='Update Alice'),
		    Choice(lambda: ctx.invoke(updateSystem), name='Update system'),
		    Choice(lambda: ctx.invoke(upgradeSystem), name='Upgrade system'),
		    Separator(line='\n------- Logs -------'),
		    Choice(lambda: ctx.invoke(reportBug), name='Enable bug report for next session'),
		    Choice(lambda: ctx.invoke(aliceLogs), name='Check Alice logs'),
		    Choice(lambda: ctx.invoke(systemLogs), name='Check system logs'),
		    Separator(line='\n------- Tools -------'),
		    Choice(lambda: ctx.invoke(reboot), name='Reboot device'),
		    Choice(lambda: ctx.invoke(uninstallSoundDevice), name='Uninstall your sound device'),
		    Choice(lambda: ctx.invoke(disableRespeakerLeds), name='Turn off Respeaker bright white leds'),
		    Choice(lambda: sys.exit(0), name='Exit')
	    ]
	).execute()

	action()
