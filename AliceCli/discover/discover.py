import socket

import click
import networkscan

from AliceCli.utils import utils
from AliceCli.utils.utils import IP_REGEX


@click.command()
@click.option('-n', '--network', required=False, type=str, default='')
def discover(network: str):
	click.clear()
	click.secho('Discovering devices on your network, please wait', fg='yellow')

	ip = IP_REGEX.search(socket.gethostbyname(socket.gethostname()))
	if not ip and not network:
		utils.printError("Could retrieve local ip addresse")
	else:
		if not network:
			network = f"{'.'.join(ip[0].split('.')[0:3])}.0/24"

		click.secho(f'Scanning network: {network}', fg='yellow')
		flag = utils.waitAnimation()
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

	utils.returnToMainMenu()
