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
import re
import subprocess
import sys

import click
from InquirerPy import prompt
from InquirerPy.separator import Separator

from AliceCli.Version import Version
from AliceCli.alice.alice import reportBug, systemctl, updateAlice
from AliceCli.install.install import installAlice, installSoundDevice, prepareSdCard, uninstallSoundDevice
from AliceCli.utils.commons import connect, discover
from AliceCli.utils.utils import aliceLogs, changeHostname, changePassword, reboot, soundTest, systemLogs, updateSystem, upgradeSystem


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

	answers = prompt(
		questions=[
			{
				'type'   : 'list',
				'name'   : 'mainMenu',
				'message': 'Please select an option',
				'choices': [
					'Discover devices on network',
					'Connect to a device',
					Separator(),
					'Prepare your SD card',
					'Change device\'s password',
					'Set device\'s name',
					'Install your sound device',
					'Sound test',
					'Install Alice',
					Separator(),
					'Start Alice',
					'Restart Alice',
					'Stop Alice',
					'Enable Alice service',
					'Disable Alice service',
					Separator(),
					'Update Alice',
					'Update system',
					'Upgrade system',
					'Reboot device',
					'Uninstall your sound device',
					'Enable bug report for next session',
					'Check Alice logs',
					'Check system logs',
					'Exit'
				]
			}
		]
	)

	if not answers:
		sys.exit(0)

	if answers['mainMenu'] == 'Exit':
		sys.exit(0)
	elif answers['mainMenu'] == 'Discover devices on network':
		ctx.invoke(discover)
	elif answers['mainMenu'] == 'Connect to a device':
		ctx.invoke(connect)
	elif answers['mainMenu'] == 'Reboot device':
		ctx.invoke(reboot)
	elif answers['mainMenu'] == 'Update system':
		ctx.invoke(updateSystem)
	elif answers['mainMenu'] == 'Upgrade system':
		ctx.invoke(upgradeSystem)
	elif answers['mainMenu'] == 'Sound test':
		ctx.invoke(soundTest)
	elif answers['mainMenu'] == 'Update Alice':
		ctx.invoke(updateAlice)
	elif answers['mainMenu'] == 'Restart Alice':
		ctx.invoke(systemctl, option='restart')
	elif answers['mainMenu'] == 'Start Alice':
		ctx.invoke(systemctl, option='start')
	elif answers['mainMenu'] == 'Stop Alice':
		ctx.invoke(systemctl, option='stop')
	elif answers['mainMenu'] == 'Enable Alice service':
		ctx.invoke(systemctl, option='enable')
	elif answers['mainMenu'] == 'Disable Alice service':
		ctx.invoke(systemctl, option='disable')
	elif answers['mainMenu'] == 'Install Alice':
		ctx.invoke(installAlice)
	elif answers['mainMenu'] == 'Install your sound device':
		ctx.invoke(installSoundDevice)
	elif answers['mainMenu'] == 'Uninstall your sound device':
		ctx.invoke(uninstallSoundDevice)
	elif answers['mainMenu'] == 'Prepare your SD card':
		ctx.invoke(prepareSdCard)
	elif answers['mainMenu'] == 'Change device\'s password':
		ctx.invoke(changePassword)
	elif answers['mainMenu'] == 'Set device\'s name':
		ctx.invoke(changeHostname)
	elif answers['mainMenu'] == 'Check Alice logs':
		ctx.invoke(aliceLogs)
	elif answers['mainMenu'] == 'Check system logs':
		ctx.invoke(systemLogs)
	elif answers['mainMenu'] == 'Enable bug report for next session':
		ctx.invoke(reportBug)
	else:
		ctx.invoke(mainMenu)
