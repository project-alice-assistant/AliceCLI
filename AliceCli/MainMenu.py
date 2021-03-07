import sys

import click
from PyInquirer import Separator, prompt

from AliceCli.alice.alice import systemctl, updateAlice
from AliceCli.install.install import installAlice, installSoundDevice, prepareSdCard, uninstallSoundDevice
from AliceCli.utils.commons import discover, connect
from AliceCli.utils.utils import changeHostname, changePassword, reboot, soundTest, updateSystem, upgradeSystem


@click.command(name='main_menu')
@click.pass_context
def mainMenu(ctx: click.Context):
	click.clear()
	answers = prompt(
		questions=[
			{
				'type': 'list',
				'name': 'mainMenu',
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
	else:
		ctx.invoke(mainMenu)
