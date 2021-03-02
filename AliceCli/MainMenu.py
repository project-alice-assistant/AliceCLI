import sys

import click
from PyInquirer import Separator, prompt

from AliceCli.alice.alice import systemctl, update_alice
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
					'Start Alice',
					'Restart Alice',
					'Stop Alice',
					'Enable Alice service',
					'Disable Alice service',
					Separator(),
					'Uninstall Alice',
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
		ctx.invoke(discover, ctx)
	elif answers['mainMenu'] == 'Connect to a device':
		ctx.invoke(connect, ctx)
	elif answers['mainMenu'] == 'Restart device':
		ctx.invoke(reboot, ctx)
	elif answers['mainMenu'] == 'Update system':
		ctx.invoke(update_system, ctx)
	elif answers['mainMenu'] == 'Upgrade system':
		ctx.invoke(upgrade_system, ctx)
	elif answers['mainMenu'] == 'Sound test':
		ctx.invoke(sound_test, ctx)
	elif answers['mainMenu'] == 'Update Alice':
		ctx.invoke(update_alice, ctx)
	elif answers['mainMenu'] == 'Restart Alice':
		ctx.invoke(systemctl, ctx, option='restart')
	elif answers['mainMenu'] == 'Start Alice':
		ctx.invoke(systemctl, ctx, option='start')
	elif answers['mainMenu'] == 'Stop Alice':
		ctx.invoke(systemctl, ctx, option='stop')
	elif answers['mainMenu'] == 'Enable Alice service':
		ctx.invoke(systemctl, ctx, option='enable')
	elif answers['mainMenu'] == 'Disable Alice service':
		ctx.invoke(systemctl, ctx, option='disable')
