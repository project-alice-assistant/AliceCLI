import json
import socket
import uuid
from pathlib import Path

from PyInquirer import prompt

import click
import paramiko
from networkscan import networkscan

from AliceCli.utils import commons
from AliceCli.utils.commons import IP_REGEX


@click.command()
@click.option('-i', '--ip_address', required=False, type=str, default='')
@click.option('-p', '--port', required=False, type=int, default=22)
@click.option('-u', '--user', required=False, type=str, default='pi')
@click.option('-pw', '--password', required=False, type=str, default='')
def connect(ip_address: str, port: int, user: str, password: str):
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
		click.secho('Successfully connected to device', fg='yellow')
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


@click.command()
@click.option('-n', '--network', required=False, type=str, default='')
def discover(network: str):
	click.clear()
	click.secho('Discovering devices on your network, please wait', fg='yellow')

	ip = IP_REGEX.search(socket.gethostbyname(socket.gethostname()))
	if not ip and not network:
		commons.printError("Could retrieve local ip addresse")
	else:
		if not network:
			network = f"{'.'.join(ip[0].split('.')[0:3])}.0/24"

		click.secho(f'Scanning network: {network}', fg='yellow')
		flag = commons.waitAnimation()
		scan = networkscan.Networkscan(network)
		scan.run()
		click.secho('Discovered potential devices:', fg='yellow')
		for device in scan.list_of_hosts_found:
			name = socket.gethostbyaddr(device)
			if not name:
				continue

			if 'projectalice' in name[0].lower() or 'raspberrypi' in name[0].lower():
				click.secho(f'{device}: {name[0].replace(".home", "")}', fg='yellow')

		flag.clear()

	commons.returnToMainMenu()
