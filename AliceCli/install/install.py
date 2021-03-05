from pathlib import Path
from typing import Tuple

import click
import psutil as psutil
import yaml
from PyInquirer import prompt
import requests

from AliceCli.utils import commons
from AliceCli.utils.decorators import checkConnection
from AliceCli.utils.utils import reboot


@click.command(name="installSoundDevice")
@click.option('-d', '--device', type=click.Choice(['respeaker2', 'respeaker4', 'respeaker4MicLinearArray', 'respeaker6MicArray'], case_sensitive=False))
@click.pass_context
@checkConnection
def installSoundDevice(ctx: click.Context, device: str):
	click.secho('Installing audio hardware', color='yellow')
	commons.waitAnimation()
	if not device:
		device = getDeviceName(ctx)
		if not device:
			return

	ctx.invoke(uninstallSoundDevice, device=device, return_to_main_menu=False)
	commons.waitAnimation()
	if device.lower() in {'respeaker2', 'respeaker4', 'respeaker4miclineararray', 'respeaker6micarray'}:
		sshCmd('git clone https://github.com/HinTak/seeed-voicecard.git ~/seeed-voicecard/')
		sshCmd('git -C ~/seeed-voicecard/ checkout v5.9 && git -C ~/seeed-voicecard/ pull')
		sshCmd('cd ~/seeed-voicecard/ && sudo ./install.sh')
		ctx.invoke(reboot, return_to_main_menu=False)
		commons.printSuccess('Device installed!')

	commons.returnToMainMenu(ctx)


@click.command(name="uninstallSoundDevice")
@click.option('-d', '--device', type=click.Choice(['respeaker2', 'respeaker4', 'respeaker4MicLinearArray', 'respeaker6MicArray'], case_sensitive=False))
@click.pass_context
@checkConnection
def uninstallSoundDevice(ctx: click.Context, device: str, return_to_main_menu: bool = True): #NOSONAR
	click.secho('Uninstalling audio hardware', color='yellow')
	commons.waitAnimation()
	if not device:
		device = getDeviceName(ctx)
		if not device:
			return

	if device.lower() in {'respeaker2', 'respeaker4', 'respeaker4miclineararray', 'respeaker6micarray'}:
		result = sshCmdWithReturn('test -d ~/seeed-voicecard/ && echo "1"')[0].readline()
		if result:
			sshCmd('cd ~/seeed-voicecard/ && sudo ./uninstall.sh')
			sshCmd('sudo rm -rf ~/seeed-voicecard/')
			ctx.invoke(reboot, return_to_main_menu=return_to_main_menu)
			commons.printSuccess('Device uninstalled!')

	if return_to_main_menu:
		commons.returnToMainMenu(ctx)


def getDeviceName(ctx: click.Context) -> str:
	answer = prompt(questions={
		'type'   : 'list',
		'name'   : 'device',
		'message': 'Select your device',
		'choices': ['respeaker2', 'respeaker4', 'respeaker4MicLinearArray', 'respeaker6MicArray']
	})

	if not answer:
		commons.printError('Cannot continue without device information')
		commons.returnToMainMenu(ctx)
		return ''

	return answer['device']



@click.command(name='installAlice')
@click.option('--force', '-f', is_flag=True)
@click.pass_context
@checkConnection
def installAlice(ctx: click.Context, force: bool):
	click.secho('\nInstalling Alice, yayyyy!', color='yellow')

	questions = [
		{
			'type': 'password',
			'name': 'adminPinCode',
			'message': 'Enter an admin pin code. It must be made of 4 characters, all digits only. (default: 1234)',
			'default': '1234',
			'validate': lambda code: code.isdigit() and int(code) < 10000
		},
		{
			'type'    : 'input',
			'name'    : 'mqttHost',
			'message' : 'Mqtt host:',
			'default' : 'localhost',
			'validate': lambda string: len(string) > 0
		},
		{
			'type'    : 'input',
			'name'    : 'mqttPort',
			'message' : 'Mqtt port:',
			'default' : '1883',
			'validate': lambda port: port.isdigit()
		},
		{
			'type'    : 'list',
			'name'    : 'activeLanguage',
			'message' : 'What language should Alice be using?',
			'default' : 'en',
			'choices' : [
				'en',
				'de',
				'fr',
				'it'
			]
		},
		{
			'type'    : 'input',
			'name'    : 'activeCountryCode',
			'message' : 'What country code should Alice be using?',
			'default' : 'US',
			'validate': lambda string: len(string) > 0
		}
	]

	answers = prompt(questions)
	if len(answers) < 5:
		commons.returnToMainMenu(ctx)
		return

	commons.waitAnimation()
	confFile = Path(Path.home(), '.pacli/projectalice.yaml')
	confFile.parent.mkdir(parents=True, exist_ok=True)

	try:
		with requests.get(url='https://raw.githubusercontent.com/project-alice-assistant/ProjectAlice/master/ProjectAlice.yaml', stream=True) as r:
			r.raise_for_status()
			with confFile.open('wb') as fp:
				for chunk in r.iter_content(chunk_size=8192):
					if chunk:
						fp.write(chunk)
	except Exception as e:
		commons.printError(f'Failed downloading ProjectAlice.yaml {e}')
		commons.returnToMainMenu(ctx)

	with confFile.open(mode='r') as f:
		try:
			confs = yaml.safe_load(f)
		except yaml.YAMLError as e:
			commons.printError(f'Failed reading projectalice.yaml {e}')
			commons.returnToMainMenu(ctx)

	confs['adminPinCode'] = int(answers['adminPinCode'])
	confs['mqttHost'] = answers['mqttHost']
	confs['mqttPort'] = int(answers['mqttPort'])
	confs['activeLanguage'] = answers['activeLanguage']
	confs['activeCountryCode'] = answers['activeCountryCode']

	with confFile.open(mode='w') as f:
		yaml.dump(confs, f)

	commons.printSuccess('Generated ProjectAlice.yaml')

	sshCmd('sudo apt-get update')
	sshCmd('sudo apt-get install git -y')
	sshCmd('git config --global user.name "An Other"')
	sshCmd('git config --global user.email "anotheruser@projectalice.io"')

	result = sshCmdWithReturn('test -d ~/ProjectAlice/ && echo "1"')[0].readline()
	if result:
		if not force:
			commons.printError('Alice seems to already exist on that host')
			answer = prompt(questions={
				'type': 'confirm',
				'message': 'Erase and reinstall',
				'name': 'confirm',
				'default': False
			})
			if not answer['confirm']:
				commons.returnToMainMenu(ctx)
				return

		commons.waitAnimation()
		sshCmd('sudo systemctl stop ProjectAlice')
		sshCmd('sudo rm -rf ~/ProjectAlice')

	sshCmd('git clone https://github.com/project-alice-assistant/ProjectAlice.git ~/ProjectAlice')
	sshCmd('git -C ~/ProjectAlice submodule init')
	sshCmd('git -C ~/ProjectAlice submodule update')
	sshCmd('git -C ~/ProjectAlice submodule foreach git checkout builds_master')
	sshCmd('git -C ~/ProjectAlice submodule foreach git pull')
	sshCmd(f'echo "{confFile.read_text()}" > ~/ProjectAlice/ProjectAlice.yaml')
	sshCmd('sudo cp ~/ProjectAlice/ProjectAlice.yaml /boot/ProjectAlice.yaml')
	sshCmd('python3 ~/ProjectAlice/main.py')

	commons.printSuccess('Alice is installing!')
	commons.returnToMainMenu(ctx)


@click.command(name='prepareSdCard')
@click.pass_context
def prepareSdCard(ctx: click.Context):

	drives = list()
	for dp in psutil.disk_partitions():
		if 'removable' not in dp.opts.lower():
			continue
		try:
			if psutil.disk_usage(dp.device).total / 1024 / 1024 < 300: # boot partitions are usually tiny
				drives.append(dp.device)
		except:
			continue # If we can't read the partition, we can't write it either

	questions = [
		{
			'type'   : 'list',
			'name'   : 'drive',
			'message': 'Select your SD card drive (boot partition)',
			'choices': drives
		},
		{
			'type'   : 'input',
			'name'   : 'ssid',
			'message': 'Please enter the name of your Wifi network',
			'validate': lambda c: len(c) > 0
		},
		{
			'type'   : 'input',
			'name'   : 'country',
			'message': 'Please enter your country code (example: CH, US, DE, FR etc)',
			'validate': lambda c: len(c) == 2
		},
		{
			'type'   : 'password',
			'name'   : 'password',
			'message': 'Please enter your Wifi network\'s key'
		}
	]

	answers = prompt(questions=questions)

	if not answers:
		commons.returnToMainMenu(ctx)

	Path(answers['drive'], 'ssh').touch()

	content = f'country={answers["country"]}\n'
	content += 'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n'
	content += 'update_config=1\n'
	content += 'network={\n'
	content += f'\tssid="{answers["ssid"]}"\n'
	content += '\tscan_ssid=1\n'
	content += f'\tpsk="{answers["password"]}"\n'
	content += '\tkey_mgmt=WPA-PSK\n'
	content += '}'
	Path(answers['drive'], 'wpa_supplicant.conf').write_text(content)

	commons.printSuccess('SD card ready, please plug it in your device and boot it!')
	commons.returnToMainMenu(ctx)


def sshCmd(cmd: str):
	stdin, stdout, stderr = commons.SSH.exec_command(cmd)
	while line := stdout.readline():
		click.secho(line, nl=False, color='yellow')


def sshCmdWithReturn(cmd: str) -> Tuple:
	stdin, stdout, stderr = commons.SSH.exec_command(cmd)
	return stdout, stderr
