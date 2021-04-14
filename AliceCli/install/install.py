#  Copyright (c) 2021
#
#  This file, install.py, is part of Project Alice CLI.
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
#  Last modified: 2021.04.13 at 14:46:45 CEST
#  Last modified by: Psycho
import platform
import subprocess
from pathlib import Path
from shutil import which
from typing import Tuple

import click
import psutil as psutil
import yaml
from PyInquirer import prompt
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

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

		sshCmd('sudo systemctl stop ProjectAlice')
		sshCmd('sudo rm -rf ~/ProjectAlice')

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
	confs['useHLC'] = False

	with confFile.open(mode='w') as f:
		yaml.dump(confs, f)

	commons.printSuccess('Generated ProjectAlice.yaml')

	commons.printInfo('Updating system')
	sshCmd('sudo apt-get update')
	sshCmd('sudo apt-get install git -y')
	sshCmd('git config --global user.name "Han Oter"')
	sshCmd('git config --global user.email "anotheruser@projectalice.io"')

	commons.printInfo('Cloning Alice')
	sshCmd('git clone https://github.com/project-alice-assistant/ProjectAlice.git ~/ProjectAlice')
	sshCmd(f'echo "{confFile.read_text()}" > ~/ProjectAlice/ProjectAlice.yaml')
	sshCmd('sudo cp ~/ProjectAlice/ProjectAlice.yaml /boot/ProjectAlice.yaml')

	commons.printInfo('Start install process')
	sshCmd('cd ~/ProjectAlice/ && python3 main.py')

	commons.printSuccess('Alice has completed the basic installation! She\'s now working further to complete the installation, let\'s see what she does!')
	commons.ctrlCExplained()

	try:
		sshCmd('tail -f /var/log/syslog & { read ; kill %1; }')
	except KeyboardInterrupt:
		commons.SSH.exec_command('\r')
		commons.returnToMainMenu(ctx)


@click.command(name='prepareSdCard')
@click.pass_context
def prepareSdCard(ctx: click.Context):

	flasherAvailable = which('balena') is not None
	downloadsPath = Path.home() / 'Downloads'
	operatingSystem = platform.system().lower()

	questions = [
		{
			'type': 'confirm',
			'message': 'Do you want to flash your SD card with Raspberry PI OS?',
			'name': 'doFlash',
			'default': False
		},
		{
			'type': 'confirm',
			'message': 'Balena-cli was not found on your system, do you want to install it?',
			'name': 'installBalena',
			'default': True,
			'when': lambda flasherAvailable: not flasherAvailable
		}
	]

	answers = prompt(questions)
	answers.setdefault('installBalena', False)

	if answers['doFlash'] and not flasherAvailable and not answers['installBalena']:
		commons.printError('Well then, I cannot flash your SD card without the appropriate tool to do it')
		commons.returnToMainMenu(ctx)
		return
	elif answers['doFlash'] and not flasherAvailable and answers['installBalena']:
		commons.printInfo('Installing Balena-cli, please wait...')

		if operatingSystem == 'windows':
			url = 'https://github.com/balena-io/balena-cli/releases/download/v12.44.9/balena-cli-v12.44.9-windows-x64-installer.exe'
		elif operatingSystem == 'linux':
			url = 'https://github.com/balena-io/balena-cli/releases/download/v12.44.9/balena-cli-v12.44.9-linux-x64-standalone.zip'
		else:
			url = 'https://github.com/balena-io/balena-cli/releases/download/v12.44.9/balena-cli-v12.44.9-macOS-x64-installer.pkg'

		destination = downloadsPath / url.split('/')[-1]
		doDownload(url=url, destination=destination)

		if operatingSystem == 'windows':
			commons.printInfo("Downloaded! I'm starting the installation, please follow the instructions and come back when it's done!")
			subprocess.Popen(str(destination).split(), shell=True)
			click.pause('Press a key when the installation process is done! Please close your terminal and restart it to continue the flashing process')
			exit(0)
		else:
			click.pause('I have no idea how to install stuff on Mac, so I have downloaded the tool for you, please install it. Oh, and contact Psycho to let him know how to install a pkg file on Mac ;-)')
			exit(0)

	images = list()
	if answers['doFlash']:
		directories = list()
		commons.printInfo('Checking for Raspberry PI OS images, please wait....')
		# Get a list of available images
		url = 'https://downloads.raspberrypi.org/raspios_lite_armhf/images/'
		page = requests.get(url)
		if page.status_code == 200:
			soup = BeautifulSoup(page.text, features='html.parser')
			directories = [url + node.get('href') for node in soup.find_all('a') if node.get('href').endswith('/')]
			if directories:
				directories.pop(0) # This is the return link, remove it...

		for directory in directories:
			page = requests.get(directory)
			if page.status_code == 200:
				soup = BeautifulSoup(page.text, features='html.parser')
				images.extend([directory + node.get('href') for node in soup.find_all('a') if node.get('href').endswith('.zip')])

		# Potential local files
		downloadsPath = Path.home() / 'Downloads'
		for file in downloadsPath.glob('*raspi*.zip'):
			images.append(str(file))


	drives = list()
	for dp in psutil.disk_partitions():
		if 'removable' not in dp.opts.lower():
			continue
		drives.append(dp.device)

	if not drives:
		commons.printError('Please insert your SD card first')
		commons.returnToMainMenu(ctx)
		return

	questions = [
		{
			'type'   : 'list',
			'name'   : 'image',
			'message': 'Select the image you want to flash',
			'choices': images,
			'when': lambda answers: answers['doFlash']
		},
		{
			'type'   : 'list',
			'name'   : 'drive',
			'message': 'Select your SD card drive',
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

	answers = prompt(questions=questions, answers=answers)

	if not answers:
		commons.returnToMainMenu(ctx)

	if answers['doFlash']:
		if answers['image'].startswith('https'):
			file = downloadsPath / answers['image'].split('/')[-1]
			doDownload(url=answers['image'], destination=file)
		else:
			file = answers['image']

		if operatingSystem == 'windows':
			subprocess.run(f'balena local flash {str(file)}'.split(), shell=True)

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


def doDownload(url: str, destination: Path):
	with destination.open(mode='wb') as f:
		response = requests.get(url, stream=True)
		size = int(response.headers.get('content-length'))

		with tqdm(total=size, unit='B', unit_scale=True, unit_divisor=1024, desc=url.split('/')[-1], initial=0, ascii=True, miniters=1) as progress:
			for data in response.iter_content(chunk_size=4096):
				f.write(data)
				progress.update(len(data))
