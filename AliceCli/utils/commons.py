import re
import sys
import time
import click
from threading import Event, Thread

from PyInquirer import prompt

from AliceCli import MainMenu

IP_REGEX = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')

def printError(text: str):
	click.secho(message=f'✘ {text}', fg='red')
	time.sleep(2)


def printSuccess(text: str):
	click.secho(message=f'✔ {text}', fg='green')
	time.sleep(2)


def waitAnimation() -> Event:
	flag = Event()
	thread = Thread(target=_animation, kwargs={'flag': flag}, daemon=True)
	thread.start()
	return flag


def _animation(flag: Event):
	animation = "|/-\\"
	idx = 0
	flag.set()
	while flag.is_set():
		click.secho(animation[idx % len(animation)] + '\r', nl=False, fg='yellow')
		idx += 1
		time.sleep(0.1)


def askReturnToMainMenu(ctx: click.Context):
	answers = prompt(
		questions=[
			{
				'type': 'list',
				'name': 'return',
				'message': 'What do you want to do now',
				'choices': [
					'Return to main menu',
					'Exit'
				]
			}
		]
	)
	if answers['return'] == 'Exit':
		sys.exit(0)
	else:
		returnToMainMenu(ctx)


def returnToMainMenu(ctx: click.Context):
	ctx.invoke(MainMenu.mainMenu)
