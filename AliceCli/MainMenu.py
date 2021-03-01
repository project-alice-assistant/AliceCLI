import sys

import click
from PyInquirer import Separator, prompt

from AliceCli.connect import connect
from AliceCli.discover import discover


def mainMenu():
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
					'Restart device',
					'Exit'
				]
			}
		]
	)

	if answers['mainMenu'] == 'Exit':
		sys.exit(0)
	elif answers['mainMenu'] == 'Discover devices on network':
		discover.discover()
	elif answers['mainMenu'] == 'Connect to a device':
		connect.connect()
