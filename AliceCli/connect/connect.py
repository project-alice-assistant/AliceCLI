import re
from pathlib import Path

from PyInquirer import prompt

import click
import paramiko

IP_REGEX = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')


@click.command()
@click.option('-i', '--ip_address', required=False, type=str, default='')
@click.option('-p', '--port', required=False, type=int, default=22)
@click.option('-u', '--user', required=False, type=str, default='pi')
@click.option('-pw', '--password', required=False, type=str, default='')
def connect(ip_address: str, port: int, user: str, password: str):
	keyFile = Path(Path.home(), '.ssh', 'id_rsa_pac')
	pubKeyFile = keyFile.with_suffix('.pub')
	remoteAuthorizedKeysFile = '~/.ssh/authorized_keys'

	def ipMissing(_answers) -> bool:
		return not ip_address or not IP_REGEX.match(ip_address)

	def askPassword(_answers) -> bool:
		return not password and not keyFile.exists()

	questions = [
		{
			'type'    : 'input',
			'name'    : 'ip_address',
			'message' : 'Please enter the device IP address',
			'validate': lambda ip: IP_REGEX.match(ip) is not None,
			'when'    : ipMissing
		},
		{
			'type'   : 'password',
			'name'   : 'password',
			'message': 'Key file not found, please enter the connection password',
			'when': askPassword
		}
	]

	answers = prompt(questions=questions)

	ip_address = answers.get('ip_address', ip_address)
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
		click.echo(f'Failed connecting to device: {e}')
	else:
		click.echo('Successfully connected to device')
		if password:
			key = paramiko.RSAKey.generate(4096)
			key.write_private_key_file(filename=str(keyFile))
			pubKeyFile.write_text(key.get_base64())
			stdin , stdout, stderr = ssh.exec_command(f"echo \"ssh-rsa {pubKeyFile.read_text()} Project Alice RSA key\" | exec sh -c 'cd ; umask 077 ; mkdir -p .ssh && cat >> {remoteAuthorizedKeysFile} || exit 1 ; if type restorecon >/dev/null 2>&1 ; then restorecon -F .ssh ${remoteAuthorizedKeysFile} ; fi'")
