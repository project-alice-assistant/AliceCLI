import sys

import click
from PyInquirer import Separator, prompt

from AliceCli.utils.utils import connect, discover, reboot, sound_test, update_system, upgrade_system


@click.command(name='main_menu')
@click.pass_context
def mainMenu(ctx: click.Context):
	click.clear()
	answers = prompt(
		questions=[
			{
				'type': 'list',
				'name': 'mainMenu',
				'message': 'This is the main menu of Alice CLI. Please select an option.',
				'choices': [
					'Discover devices on network',
					'Connect to a device',
					'Sound test',
					Separator(),
					'Install your sound device',
					'Install Alice',
					'Install Alice satellite',
					Separator(),
					'Restart Alice',
					'Restart Alice Satellite',
					Separator(),
					'Uninstall Alice',
					'Uninstall Alice satellite',
					Separator(),
					'Update Alice',
					'Update system',
					'Upgrade system',
					'Reboot device',
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
	elif answers['mainMenu'] == 'Restart device':
		ctx.invoke(reboot)
	elif answers['mainMenu'] == 'Update system':
		ctx.invoke(update_system)
	elif answers['mainMenu'] == 'Upgrade system':
		ctx.invoke(upgrade_system)
	elif answers['mainMenu'] == 'Sound test':
		ctx.invoke(sound_test)

