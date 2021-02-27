import click
import paramiko


@click.command()
@click.argument('ip_adress')
@click.option('-p', '--port', required=False, type=int, default=22)
@click.option('-u', '--user', required=False, type=str, default='pi')
@click.option('-pw', '--password', required=False, type=str, default='raspberry')
def connect(ip_adress, port, user, password):
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
		ssh.connect(ip_adress, port, user, password)
	except:
		click.echo('Failed connecting to device')
	else:
		click.echo('Successfully connected to device')
