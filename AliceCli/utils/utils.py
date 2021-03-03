import json
import socket
import time
import uuid
from pathlib import Path
from typing import Optional

from PyInquirer import prompt

import click
import paramiko
from networkscan import networkscan

from AliceCli.utils import commons
from AliceCli.utils.decorators import checkConnection


@click.command(name='connect')
@click.option('-i', '--ip_address', required=False, type=str, default='')
@click.option('-p', '--port', required=False, type=int, default=22)
@click.option('-u', '--user', required=False, type=str, default='pi')
@click.option('-pw', '--password', required=False, type=str, default='')
@click.option('-r', '--return_to_main_menu', required=False, type=bool, default=True)
@click.pass_context
def connect(ctx: click.Context, ip_address: str, port: int, user: str, password: str, return_to_main_menu: bool) -> Optional[paramiko.SSHClient]:
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
				'validate': lambda ip: commons.IP_REGEX.match(ip) is not None
			}
		]

		answers = prompt(questions=question)
		ip_address = answers['ip_address']

	data = confs['servers'].get(ip_address, dict()).get('keyFile')
	if data:
		user = confs['servers'][ip_address]['user']
		keyFile = Path(Path.home(), f".ssh/{confs['servers'][ip_address]['keyFile']}")

		if not keyFile.exists():
			commons.printError('Declared server is using a non existing RSA key file, removing entry and asking for password.')
			confs['servers'].pop(ip_address, None)
			keyFile = None
	else:
		keyFile = None

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
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)

		if password:
			ssh.connect(hostname=ip_address, port=port, username=user, password=password)
		else:
			key = paramiko.RSAKey.from_private_key_file(str(keyFile))
			ssh.connect(hostname=ip_address, port=port, username=user, pkey=key)

	except Exception as e:
		commons.printError(f'Failed connecting to device: {e}')
	else:
		commons.printSuccess('Successfully connected to device')
		commons.SSH = ssh
		if ip_address not in confs['servers']:
			filename = f'id_rsa_{str(uuid.uuid4())}'
			keyFile = Path(Path.home(), f'.ssh/{filename}')
			confs['servers'][ip_address] = {
				'keyFile': filename,
				'user': user
			}
			confFile.write_text(json.dumps(confs))

			key = paramiko.RSAKey.generate(4096)
			key.write_private_key_file(filename=str(keyFile))

			pubKeyFile = keyFile.with_suffix('.pub')
			pubKeyFile.write_text(key.get_base64())
			ssh.exec_command(f"echo \"ssh-rsa {pubKeyFile.read_text()} Project Alice RSA key\" | exec sh -c 'cd ; umask 077 ; mkdir -p .ssh && cat >> {remoteAuthorizedKeysFile} || exit 1 ; if type restorecon >/dev/null 2>&1 ; then restorecon -F .ssh ${remoteAuthorizedKeysFile} ; fi'")

		if not return_to_main_menu:
			return ssh

	commons.returnToMainMenu(ctx)


@click.command(name='discover')
@click.option('-n', '--network', required=False, type=str, default='')
@click.option('-a', '--all_devices', is_flag=True)
@click.pass_context
def discover(ctx: click.Context, network: str, all_devices: bool):
	click.clear()
	click.secho('Discovering devices on your network, please wait', fg='yellow')

	ip = commons.IP_REGEX.search(socket.gethostbyname(socket.gethostname()))
	if not ip and not network:
		commons.printError("Could retrieve local ip addresse")
	else:
		if not network:
			network = f"{'.'.join(ip[0].split('.')[0:3])}.0/24"

		click.secho(f'Scanning network: {network}', fg='yellow')
		flag = commons.waitAnimation()
		scan = networkscan.Networkscan(network)
		scan.run()

		if all_devices:
			click.secho('Discovered devices:', fg='yellow')
		else:
			click.secho('Discovered potential devices:', fg='yellow')
		for device in scan.list_of_hosts_found:
			name = socket.gethostbyaddr(device)
			if not name:
				continue

			if all_devices or (not all_devices and ('projectalice' in name[0].lower() or 'raspberrypi' in name[0].lower())):
				click.secho(f'{device}: {name[0].replace(".home", "")}', fg='yellow')

		flag.clear()

	click.pause()
	commons.returnToMainMenu(ctx)


@click.command(name='reboot')
@click.pass_context
@checkConnection
def reboot(ctx: click.Context):
	click.secho('Rebooting device, please wait', color='yellow')

	flag = commons.waitAnimation()
	commons.SSH.exec_command('sudo reboot')

	i = 0
	while i < 10:
		time.sleep(5)
		test = connect()
		if test:
			commons.printSuccess('Device rebooted!')
			commons.returnToMainMenu(ctx)
			flag.clear()
			return
		i += 1

	flag.clear()
	commons.printError('Failed rebooting device')
	commons.returnToMainMenu(ctx)


@click.command(name='updateSystem')
@click.pass_context
@checkConnection
def updateSystem(ctx: click.Context):
	click.secho('Updating device\'s system, please wait', color='yellow')

	flag = commons.waitAnimation()
	stdin, stdout, stderr = commons.SSH.exec_command('sudo apt-get update && sudo apt-get upgrade -y')
	line = stdout.readline()
	while line:
		click.secho(line, nl=False, color='yellow')
		line = stdout.readline()

	flag.clear()
	commons.printSuccess('Device updated!')
	commons.returnToMainMenu(ctx)


@click.command(name='upgradeSystem')
@click.pass_context
@checkConnection
def upgradeSystem(ctx: click.Context):
	click.secho('Upgrading device\'s system, please wait', color='yellow')

	flag = commons.waitAnimation()
	stdin, stdout, stderr = commons.SSH.exec_command('sudo apt-get update && sudo apt-get dist-upgrade -y')
	line = stdout.readline()
	while line:
		click.secho(line, nl=False, color='yellow')
		line = stdout.readline()

	flag.clear()
	commons.printSuccess('Device upgraded!')
	ctx.invoke(reboot)


@click.command(name='soundtest')
@click.pass_context
@checkConnection
def soundTest(ctx: click.Context):
	click.secho('Testing sound output...', color='yellow')

	flag = commons.waitAnimation()
	stdin, stdout, stderr = commons.SSH.exec_command('sudo aplay /usr/share/sounds/alsa/Front_Center.wav')
	line = stdout.readline()
	click.secho(line)
	flag.clear()
	commons.returnToMainMenu(ctx)
