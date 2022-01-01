#  Copyright (c) 2021
#
#  This file, commons.py, is part of Project Alice CLI.
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
#  Last modified: 2021.03.07 at 13:31:43 CET
#  Last modified by: Psycho
import click
import json
import paramiko
import re
import requests
import socket
import sys
import time
import uuid
from PyInquirer import prompt
from networkscan import networkscan
from pathlib import Path
from threading import Event, Thread
from typing import Optional, Tuple

from AliceCli.Version import Version


IP_REGEX = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
SSH: Optional[paramiko.SSHClient] = None
CONNECTED_TO: str = ''
ANIMATION_FLAG = Event()
ANIMATION_THREAD: Optional[Thread] = None


@click.command(name='discover')
@click.option('-n', '--network', required=False, type=str, default='')
@click.option('-a', '--all_devices', is_flag=True)
@click.pass_context
def discover(ctx: click.Context, network: str, all_devices: bool, return_to_main_menu: bool = True):  # NOSONAR
	click.clear()
	click.secho('Discovering devices on your network, please wait', fg='yellow')

	ip = IP_REGEX.search(socket.gethostbyname(socket.gethostname()))
	if not ip and not network:
		printError("Couldn't retrieve local ip address")
	else:
		if not network:
			network = f"{'.'.join(ip[0].split('.')[0:3])}.0/24"

		click.secho(f'Scanning network: {network}', fg='yellow')
		waitAnimation()
		scan = networkscan.Networkscan(network)
		scan.run()

		if all_devices:
			click.secho('Discovered devices:', fg='yellow')
		else:
			click.secho('Discovered potential devices:', fg='yellow')

		devices = list()
		for device in scan.list_of_hosts_found:
			try:
				name = socket.gethostbyaddr(device)
				if not name:
					continue

				if all_devices or (not all_devices and ('projectalice' in name[0].lower() or 'raspberrypi' in name[0].lower())):
					click.secho(f'{device}: {name[0].replace(".home", "")}', fg='yellow')
					devices.append(device)
			except:
				continue  # If no name, we don't need the device anyway

		stopAnimation()

		devices.append('Return to main menu')  # NOSONAR
		answer = prompt(questions={
			'type'   : 'list',
			'name'   : 'device',
			'message': 'Select the device you want to connect to',
			'choices': devices
		})

		if not answer or answer['device'] == 'Return to main menu':
			returnToMainMenu(ctx)

		if answer['device'] != 'Return to main menu':
			ctx.invoke(connect, ip_address=answer['device'], return_to_main_menu=return_to_main_menu)

	if return_to_main_menu:
		returnToMainMenu(ctx)


@click.command(name='connect')
@click.option('-i', '--ip_address', required=False, type=str, default='')
@click.option('-p', '--port', required=False, type=int, default=22)
@click.option('-u', '--user', required=False, type=str)
@click.option('-pw', '--password', required=False, type=str, default='')
@click.option('-r', '--return_to_main_menu', required=False, type=bool, default=True)
@click.pass_context
def connect(ctx: click.Context, ip_address: str, port: int, user: str, password: str, return_to_main_menu: bool, noExceptHandling: bool = False) -> Optional[paramiko.SSHClient]:  # NOSONAR
	global SSH, IP_REGEX, CONNECTED_TO
	remoteAuthorizedKeysFile = '~/.ssh/authorized_keys'
	confFile = Path(Path.home(), '.pacli/configs.json')
	confFile.parent.mkdir(parents=True, exist_ok=True)
	if not confFile.exists():
		confs = dict()
		confs['servers'] = dict()
		confFile.write_text(json.dumps(confs))
	else:
		confs = json.loads(confFile.read_text())

	if not ip_address:
		question = [
			{
				'type'    : 'input',
				'name'    : 'ip_address',
				'message' : 'Please enter the device IP address',
				'validate': lambda ip: IP_REGEX.match(ip) is not None
			}
		]

		answers = prompt(questions=question)
		ip_address = answers['ip_address']

	data = confs['servers'].get(ip_address, dict()).get('keyFile')
	if data:
		user = confs['servers'][ip_address]['user']
		keyFile = Path(Path.home(), f".ssh/{confs['servers'][ip_address]['keyFile']}")

		if not keyFile.exists():
			printError('Declared server is using a non existing RSA key file, removing entry and asking for password.')
			confs['servers'].pop(ip_address, None)
			keyFile = None
	else:
		keyFile = None

	if not keyFile and not user:
		question = [
			{
				'type'   : 'input',
				'name'   : 'user',
				'message': 'Please enter username'
			}
		]

		answers = prompt(questions=question)
		user = answers.get('user', user)

	if not keyFile and not password:
		question = [
			{
				'type'   : 'password',
				'name'   : 'password',
				'message': 'Please enter the connection password'
			}
		]

		answers = prompt(questions=question)
		password = answers.get('password', password)

	try:
		if SSH:
			disconnect()

		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)

		waitAnimation()

		if password:
			ssh.connect(hostname=ip_address, port=port, username=user, password=password)
		else:
			key = paramiko.RSAKey.from_private_key_file(str(keyFile))
			ssh.connect(hostname=ip_address, port=port, username=user, pkey=key)

	except Exception as e:
		if not noExceptHandling:
			printError(f'Failed connecting to device: {e}')
			if ip_address in confs['servers'] and not password:
				confs['servers'].pop(ip_address, None)
				confFile.write_text(json.dumps(confs))
				ctx.invoke(connect, ip_address=ip_address, user=user, return_to_main_menu=return_to_main_menu)
				return
		else:
			raise
	else:
		printSuccess('Successfully connected to device')
		SSH = ssh
		CONNECTED_TO = ip_address
		if ip_address not in confs['servers']:
			filename = f'id_rsa_{str(uuid.uuid4())}'
			keyFile = Path(Path.home(), f'.ssh/{filename}')
			confs['servers'][ip_address] = {
				'keyFile': filename,
				'user'   : user
			}
			confFile.write_text(json.dumps(confs))

			key = paramiko.RSAKey.generate(4096)
			key.write_private_key_file(filename=str(keyFile))

			pubKeyFile = keyFile.with_suffix('.pub')
			pubKeyFile.write_text(key.get_base64())
			ssh.exec_command(f"echo \"ssh-rsa {pubKeyFile.read_text()} Project Alice RSA key\" | exec sh -c 'cd ; umask 077 ; mkdir -p .ssh && cat >> {remoteAuthorizedKeysFile} || exit 1 ; if type restorecon >/dev/null 2>&1 ; then restorecon -F .ssh ${remoteAuthorizedKeysFile} ; fi'")

		if not return_to_main_menu:
			return ssh

	if return_to_main_menu:
		returnToMainMenu(ctx)


def printError(text: str):
	ANIMATION_FLAG.clear()
	click.secho(message=f'✘ {text}', fg='red')
	time.sleep(2)


def printSuccess(text: str):
	ANIMATION_FLAG.clear()
	click.secho(message=f'✔ {text}', fg='green')
	time.sleep(2)


def printInfo(text: str):
	ANIMATION_FLAG.clear()
	click.secho(message=f'▷ {text}', fg='yellow')
	time.sleep(0.5)


def disconnect():
	global SSH, CONNECTED_TO
	if SSH:
		SSH.close()
		SSH = None
		CONNECTED_TO = ''
		printSuccess('Disconnected')


def waitAnimation():
	global ANIMATION_THREAD

	if ANIMATION_FLAG.is_set():
		ANIMATION_FLAG.clear()

	if ANIMATION_THREAD:
		ANIMATION_THREAD.join(timeout=1)

	ANIMATION_THREAD = Thread(target=_animation, daemon=True)
	ANIMATION_THREAD.start()
	time.sleep(1)


def ctrlCExplained():
	global ANIMATION_THREAD

	if ANIMATION_FLAG.is_set():
		ANIMATION_FLAG.clear()

	if ANIMATION_THREAD:
		ANIMATION_THREAD.join(timeout=1)

	ANIMATION_THREAD = Thread(target=_ctrlCExplained, daemon=True)
	ANIMATION_THREAD.start()
	time.sleep(1)


def stopAnimation():
	ANIMATION_FLAG.clear()


def _animation():
	animation = '|/-\\'
	idx = 0
	ANIMATION_FLAG.set()
	while ANIMATION_FLAG.is_set():
		click.secho(animation[idx % len(animation)] + '\r', nl=False, fg='yellow')
		idx += 1
		time.sleep(0.1)


def _ctrlCExplained():
	ANIMATION_FLAG.set()
	while ANIMATION_FLAG.is_set():
		try:
			click.secho(f'\rPress CTRL-C to quit\r', nl=False, fg='yellow')
			time.sleep(0.1)
		except KeyboardInterrupt:
			ANIMATION_FLAG.clear()
			raise KeyboardInterrupt


def askReturnToMainMenu(ctx: click.Context):
	answers = prompt(
		questions=[
			{
				'type'   : 'list',
				'name'   : 'return',
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


def returnToMainMenu(ctx: click.Context, pause: bool = False, message: str = ''):
	import AliceCli.MainMenu as MainMenu

	stopAnimation()
	if pause:
		click.echo(message)
		click.pause('Press any key to continue')

	ctx.invoke(MainMenu.mainMenu)


def validateHostname(hostname: str) -> str:
	if not hostname:
		raise click.BadParameter('Hostname cannot be empty')

	if len(hostname) > 253:
		raise click.BadParameter('Hostname maximum length is 253')

	allowed = re.compile(r'^([\w]*)$', re.IGNORECASE)
	if allowed.match(hostname):
		return hostname
	else:
		raise click.BadParameter('Hostname cannot contain special characters')


def sshCmd(cmd: str, hide: bool = False):
	stdin, stdout, stderr = SSH.exec_command(cmd)

	while line := stdout.readline():
		if not hide:
			click.secho(line, nl=False, color='yellow')


def sshCmdWithReturn(cmd: str) -> Tuple:
	stdin, stdout, stderr = SSH.exec_command(cmd)
	return stdout, stderr


def getUpdateSource(definedSource: str) -> str:
	updateSource = 'master'
	if definedSource in {'master', 'release'}:
		return updateSource

	# noinspection PyUnboundLocalVariable
	req = requests.get('https://api.github.com/repos/project-alice-assistant/ProjectAlice/branches')
	result = req.json()

	versions = list()
	for branch in result:
		repoVersion = Version.fromString(branch['name'])

		releaseType = repoVersion.releaseType
		if not repoVersion.isVersionNumber \
				or definedSource == 'rc' and releaseType in {'b', 'a'} \
				or definedSource == 'beta' and releaseType == 'a':
			continue

		versions.append(repoVersion)

	if versions:
		versions.sort(reverse=True)
		updateSource = versions[0]

	return str(updateSource)
