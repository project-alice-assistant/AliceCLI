#  Copyright (c) 2021
#
#  This file, install.py, is part of Project Alice.
#
#  Project Alice is free software: you can redistribute it and/or modify
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
#  Last modified: 2021.07.31 at 15:54:28 CEST
import os
import platform
import subprocess
import time
import zipfile
from pathlib import Path
from shutil import which

import click
import psutil
import requests
import yaml
from InquirerPy import prompt
from tqdm import tqdm

from AliceCli.utils import commons
from AliceCli.utils.commons import sshCmd, sshCmdWithReturn
from AliceCli.utils.decorators import checkConnection
from AliceCli.utils.utils import reboot, systemLogs


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
	sshCmd('sudo apt-get install git -y')
	if device.lower() in {'respeaker2', 'respeaker4', 'respeaker4miclineararray', 'respeaker6micarray'}:
		sshCmd('git clone https://github.com/HinTak/seeed-voicecard.git ~/seeed-voicecard/')
		sshCmd('git -C ~/seeed-voicecard/ checkout v5.9 && git -C ~/seeed-voicecard/ pull')
		sshCmd('cd ~/seeed-voicecard/ && sudo ./install.sh')
		ctx.invoke(reboot, return_to_main_menu=False)
		commons.printSuccess('Sound device installed!')

	commons.returnToMainMenu(ctx, pause=True)


@click.command(name="uninstallSoundDevice")
@click.option('-d', '--device', type=click.Choice(['respeaker2', 'respeaker4', 'respeaker4MicLinearArray', 'respeaker6MicArray'], case_sensitive=False))
@click.pass_context
@checkConnection
def uninstallSoundDevice(ctx: click.Context, device: str, return_to_main_menu: bool = True):  # NOSONAR
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
			commons.printSuccess('Sound device uninstalled!')

	if return_to_main_menu:
		commons.returnToMainMenu(ctx, pause=True)


def getDeviceName(ctx: click.Context) -> str:
	answer = prompt(questions={
		'type'   : 'list',
		'name'   : 'device',
		'message': 'Select your device',
		'choices': ['respeaker2', 'respeaker4', 'respeaker4MicLinearArray', 'respeaker6MicArray']
	})

	if not answer:
		commons.printError('Cannot continue without device information')
		commons.returnToMainMenu(ctx, pause=True)
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
				'type'   : 'confirm',
				'message': 'Erase and reinstall',
				'name'   : 'confirm',
				'default': False
			})
			if not answer['confirm']:
				commons.returnToMainMenu(ctx)
				return

		sshCmd('sudo systemctl stop ProjectAlice')
		sshCmd('sudo rm -rf ~/ProjectAlice')

	questions = [
		{
			'type'    : 'password',
			'name'    : 'adminPinCode',
			'message' : 'Enter an admin pin code. It must be made of 4 characters, all digits only. (default: 1234)',
			'default' : '1234',
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
			'type'   : 'list',
			'name'   : 'activeLanguage',
			'message': 'What language should Alice be using?',
			'default': 'en',
			'choices': [
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
		},
		{
			'type'   : 'list',
			'name'   : 'releaseType',
			'message': 'What releases do you want to receive? If you are unsure, LEAVE THIS TO MASTER',
			'default': 'master',
			'choices': [
				'master',
				'rc',
				'beta',
				'alpha'
			]
		},
		{
			'type'   : 'list',
			'name'   : 'audioDevice',
			'message': 'Select your audio hardware if listed',
			'default': 'respeaker2',
			'choices': [
				'usbMic',
				'respeaker2',
				'respeaker4',
				'respeaker6MicArray',
				'respeaker7',
				'respeakerCoreV2',
				'googleAIY',
				'googleAIY2',
				'matrixCreator',
				'matrixVoice',
				'ps3eye',
				'jabra410',
				'none of the above'
			]
		},
		{
			'type'   : 'confirm',
			'message': 'Did you already install your sound hardware using Alice CLI or confirmed it to be working?',
			'name'   : 'soundInstalled',
			'default': False
		},
		{
			'type'   : 'confirm',
			'message': 'Do you want to install HLC? HLC can pilot leds such as the ones on Respeakers to provide visual feedback.',
			'name'   : 'installHLC',
			'default': False
		},
		{
			'type'   : 'confirm',
			'message': 'Do you want to set more advanced configs? If you do, DO NOT ABORT IN THE MIDDLE!',
			'name'   : 'advancedConfigs',
			'default': False
		},
		{
			'type'   : 'list',
			'message': 'Select the ASR engine you want to use',
			'name'   : 'asr',
			'choices': [
				'Google',
				'Snips (English only!)',
				'Coqui',
				'Deepspeech',
				'Pocketsphinx'
			],
			'when'   : lambda userAnswers: userAnswers['advancedConfigs']
		},
		{
			'type'   : 'list',
			'message': 'Select the TTS engine you want to use',
			'name'   : 'tts',
			'choices': [
				'Pico',
				'Mycroft',
				'Amazon',
				'Google',
				'Watson'
			],
			'when'   : lambda userAnswers: userAnswers['advancedConfigs']
		},
		{
			'type'   : 'password',
			'message': 'Enter your AWS access key',
			'name'   : 'awsAccessKey',
			'when'   : lambda userAnswers: userAnswers['advancedConfigs'] and userAnswers['tts'] == 'Amazon'
		},
		{
			'type'   : 'password',
			'message': 'Enter your AWS secret key',
			'name'   : 'awsSecretKey',
			'when'   : lambda userAnswers: userAnswers['advancedConfigs'] and userAnswers['tts'] == 'Amazon'
		},
		{
			'type'   : 'input',
			'message': 'Enter your Google service file path',
			'name'   : 'googleServiceFile',
			'when'   : lambda userAnswers: userAnswers['advancedConfigs'] and (userAnswers['asr'] == 'Google' or userAnswers['tts'] == 'Google')
		},
		{
			'type'   : 'confirm',
			'message': 'Do you want Alice to use short replies?',
			'name'   : 'shortReplies',
			'default': False,
			'when'   : lambda userAnswers: userAnswers['advancedConfigs']
		},
		{
			'type'   : 'confirm',
			'message': 'Do you want to activate the developer mode?',
			'name'   : 'devMode',
			'default': False,
			'when'   : lambda userAnswers: userAnswers['advancedConfigs']
		},
		{
			'type'   : 'input',
			'message': 'Enter your Github username. This is used for skill development. If not needed, leave blank',
			'name'   : 'githubUsername',
			'default': '',
			'when'   : lambda userAnswers: userAnswers['advancedConfigs']
		},
		{
			'type'   : 'password',
			'message': 'Enter your Github access token. This is used for skill development',
			'name'   : 'githubToken',
			'when'   : lambda userAnswers: userAnswers['advancedConfigs'] and userAnswers['githubUsername']
		},
		{
			'type'   : 'confirm',
			'message': 'Enable telemetry data storing?',
			'name'   : 'enableDataStoring',
			'default': True,
			'when'   : lambda userAnswers: userAnswers['advancedConfigs']
		},
		{
			'type'   : 'confirm',
			'message': 'Enable skill auto update?',
			'name'   : 'skillAutoUpdate',
			'default': True,
			'when'   : lambda userAnswers: userAnswers['advancedConfigs']
		}
	]

	answers = prompt(questions)
	if len(answers) < 10:
		commons.returnToMainMenu(ctx)
		return

	commons.waitAnimation()
	confFile = Path(Path.home(), '.pacli/projectalice.yaml')
	confFile.parent.mkdir(parents=True, exist_ok=True)

	updateSource = commons.getUpdateSource(answers['releaseType'])

	try:
		with requests.get(url=f'https://raw.githubusercontent.com/project-alice-assistant/ProjectAlice/{updateSource}/ProjectAlice.yaml', stream=True) as r:
			r.raise_for_status()
			with confFile.open('wb') as fp:
				for chunk in r.iter_content(chunk_size=8192):
					if chunk:
						fp.write(chunk)
	except Exception as e:
		commons.printError(f'Failed downloading ProjectAlice.yaml {e}')
		commons.returnToMainMenu(ctx, pause=True)

	with confFile.open(mode='r') as f:
		try:
			confs = yaml.safe_load(f)
		except yaml.YAMLError as e:
			commons.printError(f'Failed reading projectalice.yaml {e}')
			commons.returnToMainMenu(ctx, pause=True)

	confs['adminPinCode'] = str(int(answers['adminPinCode'])).zfill(4)
	confs['mqttHost'] = answers['mqttHost']
	confs['mqttPort'] = int(answers['mqttPort'])
	confs['activeLanguage'] = answers['activeLanguage']
	confs['activeCountryCode'] = answers['activeCountryCode']
	confs['useHLC'] = answers['installHLC']
	confs['aliceUpdateChannel'] = answers['releaseType']
	confs['skillsUpdateChannel'] = answers['releaseType']
	confs['ttsLanguage'] = f'{answers["activeLanguage"].lower()}-{answers["activeCountryCode"].upper()}'

	if answers['soundInstalled']:
		confs['installSound'] = False
		if answers['audioDevice'] != 'none of the above':
			confs['audioHardware'][answers['audioDevice']] = True
	else:
		confs['installSound'] = True

	confs['asr'] = answers.get('asr', 'coqui').lower()
	confs['awsAccessKey'] = answers.get('awsAccessKey', '')
	confs['awsSecretKey'] = answers.get('awsSecretKey', '')
	confs['tts'] = answers.get('tts', 'pico').lower()
	confs['shortReplies'] = answers.get('shortReplies', False)
	confs['devMode'] = answers.get('devMode', False)
	confs['githubUsername'] = answers.get('githubUsername', '')
	confs['githubToken'] = answers.get('githubToken', '')
	confs['enableDataStoring'] = answers.get('enableDataStoring', True)
	confs['skillAutoUpdate'] = answers.get('skillAutoUpdate', True)

	if 'googleServiceFile' in answers and Path(answers.get('googleServiceFile')).exists():
		confs['googleServiceFile'] = Path(answers['googleServiceFile']).read_text()

	if answers['advancedConfigs']:
		if answers['asr'].lower() == 'google':
			confs['keepASROffline'] = False
		if answers['tts'].lower() in ['amazon', 'google', 'watson']:
			confs['keepTTSOffline'] = False

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

	#sshCmd('sudo rm ~/ProjectAlice/ProjectAlice.yaml')
	sftp = commons.SSH.open_sftp()
	sftp.put(str(confFile), '/home/pi/ProjectAlice/ProjectAlice.yaml')
	sftp.close()

	#sshCmd(f'echo "{confFile.read_text()}" > ~/ProjectAlice/ProjectAlice.yaml', hide=True)
	sshCmd('sudo rm /boot/ProjectAlice.yaml')
	sshCmd('sudo cp ~/ProjectAlice/ProjectAlice.yaml /boot/ProjectAlice.yaml')

	commons.printInfo('Start install process')
	sshCmd('cd ~/ProjectAlice/ && python3 main.py')

	commons.printSuccess('Alice has completed the basic installation! She\'s now working further to complete the installation, let\'s see what she does!')
	ctx.invoke(systemLogs)


@click.command(name='prepareSdCard')
@click.pass_context
def prepareSdCard(ctx: click.Context):  # NOSONAR
	operatingSystem = platform.system().lower()

	balenaExecutablePath = which('balena')
	if balenaExecutablePath is None and operatingSystem == 'linux':
		balenaExecutablePath = str(Path.joinpath(Path.cwd(), 'balena-cli', 'balena'))  # default install path

	flasherAvailable = Path(balenaExecutablePath).exists()
	downloadsPath = Path.home() / 'Downloads'


	questions = [
		{
			'type'   : 'confirm',
			'message': 'Do you want to flash your SD card with Raspberry PI OS?',
			'name'   : 'doFlash',
			'default': False
		},
		{
			'type'   : 'confirm',
			'message': 'balena-cli was not found on your system. It is required for flashing SD cards, do you want to install it?',
			'name'   : 'installBalena',
			'default': True,
			'when'   : lambda _: not flasherAvailable
		}
	]

	answers = prompt(questions)
	answers.setdefault('installBalena', True)

	if not answers or 'doFlash' not in answers:
		commons.returnToMainMenu(ctx)
		return

	if answers['doFlash'] and not flasherAvailable and not answers['installBalena']:
		commons.returnToMainMenu(ctx, pause=True, message='Well then, I cannot flash your SD card without the appropriate tool to do it')
		return
	elif answers['doFlash'] and not flasherAvailable and answers['installBalena']:
		commons.printInfo('Installing Balena-cli, please wait...')
		balenaVersion = 'v13.1.1'
		if operatingSystem == 'windows':
			url = f'https://github.com/balena-io/balena-cli/releases/download/{balenaVersion}/balena-cli-{balenaVersion}-windows-x64-installer.exe'
		elif operatingSystem == 'linux':
			url = f'https://github.com/balena-io/balena-cli/releases/download/{balenaVersion}/balena-cli-{balenaVersion}-linux-x64-standalone.zip'
		else:
			url = f'https://github.com/balena-io/balena-cli/releases/download/{balenaVersion}/balena-cli-{balenaVersion}-macOS-x64-installer.pkg'

		destination = downloadsPath / url.split('/')[-1]

		if destination.exists():
			commons.printInfo(f'Skipping download, using existing: {destination}')
		else:
			commons.printInfo("Downloading...")
			doDownload(url=url, destination=destination)

		if operatingSystem == 'windows':
			commons.printInfo("Starting the installation, please follow the instructions and come back when it's done!")
			subprocess.Popen(str(destination).split(), shell=True)
			click.pause('Press a key when the installation process is done! Please close your terminal and restart it to continue the flashing process')
			exit(0)
		elif operatingSystem == 'linux':
			executablePath = Path(balenaExecutablePath)
			commons.printInfo(f"Install dir: {executablePath.parent}")
			commons.printInfo(f'Extracting {destination} to {executablePath.name}...')
			archive = zipfile.ZipFile(destination)
			archive.extractall()  # extract to ./balena-cli/ i.e. sub dir of working directory.
			commons.printInfo('Setting ./balena-cli/belena as executable...')
			# set executable permission
			# from https://stackoverflow.com/questions/12791997/how-do-you-do-a-simple-chmod-x-from-within-python
			executablePath.chmod(509)  # now shell `./balena-cli/balena version` works
			commons.printInfo('Adding ./balena-cli to PATH...')
			os.environ['PATH'] += os.pathsep + str(executablePath.parent)
			sysPath = os.environ['PATH']
			commons.printInfo(f'New PATH: {sysPath}')
			click.pause('Installation Done. Press a key')
		else:
			click.pause('I have no idea how to install stuff on Mac, so I have downloaded the tool for you, please install it. Oh, and contact Psycho to let him know how to install a pkg file on Mac ;-)')
			exit(0)

	images = list()
	if answers['doFlash']:
		commons.printInfo('Checking for Raspberry PI OS images, please wait....')
		# Potential local files
		downloadsPath = Path.home() / 'Downloads'
		for file in downloadsPath.glob('*raspi*.zip'):
			images.append(str(file))

		images.append('https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-05-28/2021-05-07-raspios-buster-armhf-lite.zip')

		# Deactivated for now, we enforce Buster only!
		# directories = list()
		# Get a list of available images online
		# url = 'https://downloads.raspberrypi.org/raspios_lite_armhf/images/'
		# page = requests.get(url)
		# if page.status_code == 200:
		# 	soup = BeautifulSoup(page.text, features='html.parser')
		# 	directories = [url + node.get('href') for node in soup.find_all('a') if node.get('href').endswith('/')]
		# 	if directories:
		# 		directories.pop(0)  # This is the return link, remove it...
		#
		# for directory in directories:
		# 	page = requests.get(directory)
		# 	if page.status_code == 200:
		# 		soup = BeautifulSoup(page.text, features='html.parser')
		# 		images.extend([directory + node.get('href') for node in soup.find_all('a') if node.get('href').endswith('.zip')])

	commons.printInfo('Checking for available SD card drives, please wait....')
	drives = dict()
	if operatingSystem == 'linux':
		balenaCommand = f'{balenaExecutablePath} util available-drives'
		driveSep = os.path.sep  # typically '/'
	else:
		balenaCommand = 'balena util available-drives'
		driveSep = '\\'
	output = subprocess.run(balenaCommand.split(), capture_output=True, shell=True).stdout.decode()
	for line in output.split('\n'):
		if not line.startswith(driveSep):
			continue
		drives[line] = line.split(' ')[0]

	if not drives:
		commons.returnToMainMenu(ctx, pause=True, message='Please insert your SD card first')
		return

	questions = [
		{
			'type'   : 'list',
			'name'   : 'image',
			'message': 'Select the image you want to flash. Keep in mind we only officially support the "Buster" Debian distro!',
			'choices': images,
			'when'   : lambda _: answers['doFlash']
		},
		{
			'type'   : 'list',
			'name'   : 'drive',
			'message': 'Select your SD card drive',
			'choices': drives
		},
		{
			'type'    : 'input',
			'name'    : 'ssid',
			'message' : 'Enter the name of your Wifi network',
			'validate': lambda c: len(c) > 0
		},
		{
			'type'   : 'password',
			'name'   : 'password',
			'message': 'Enter your Wifi network\'s key'
		},
		{
			'type'    : 'input',
			'name'    : 'country',
			'message' : 'Enter your country code (example: CH, US, DE, FR etc)',
			'validate': lambda c: len(c) == 2
		}
	]

	newAnswers = prompt(questions=questions)

	if not newAnswers:
		commons.returnToMainMenu(ctx)
		return

	answers = {**answers, **newAnswers}

	# We need the value, not the full definition of the drive...
	answers['drive'] = drives[answers['drive']]

	commons.printInfo("Ok, let's do this!")
	if answers['doFlash']:
		if answers['image'].startswith('https'):
			file = downloadsPath / answers['image'].split('/')[-1]
			doDownload(url=answers['image'], destination=file)
		else:
			file = answers['image']
		if operatingSystem == 'windows' or operatingSystem == 'linux':
			if operatingSystem == 'linux':
				# this only works on distros with "sudo" support.
				balenaCommand = f'sudo {balenaExecutablePath} local flash {str(file)} --drive {answers["drive"]} --yes'
			else:
				balenaCommand = f'balena local flash {str(file)} --drive {answers["drive"]} --yes'.split()
			subprocess.run(balenaCommand, shell=True)
			time.sleep(5)
		else:
			commons.returnToMainMenu(ctx, pause=True, message='Flashing only supported on Windows and Linux systems for now. If you have the knowledge to implement it on other systems, feel free to pull request!')
			return
	click.pause("Flashing complete. Please eject, unplug and replug your SD back, then press any key to continue...")

	drives = list()
	drive = ''
	if operatingSystem == 'linux':
		# typically, boot partition is the first increment of SD device
		# e.g. on /dev/sda drive /dev/sda1 is "boot" and /dev/sda2 is "rootfs"
		# Lookup up the boot mount point path via lsblk

		lsblkCommand = f'sudo lsblk --noheadings --list {answers["drive"]}'
		output = subprocess.run(lsblkCommand, capture_output=True, shell=True).stdout.decode()
		for line in output.split('\n'):
			mountPoint = line.split(' ')[-1]
			if not mountPoint.startswith(driveSep):
				continue
			drive = mountPoint
			break  # just take the first one
		if not drive or not Path(drive).exists():
			commons.printError(f'For some reason I cannot find the SD boot partition mount point {drive}.')
			commons.returnToMainMenu(ctx, pause=True, message="I'm really sorry, but I just can't continue without this info, sorry for wasting your time...")
	else:
		while not drives:
			i = 0
			for dp in psutil.disk_partitions():
				i += 1
				if 'rw,removable' not in dp.opts.lower():
					continue
				drives.append(dp.device)
				if i == int(answers['drive'][-1]):
					drive = dp.device

			if not drives:
				if i < 5:
					commons.printError('For some reason I cannot find the SD boot partition. Please eject then unplug, replug your SD back and press any key to continue')
					click.pause()
				else:
					break

	if not drive:
		commons.printError('Something went weird flashing/writing on your SD card, sorry, I cannot find the SD card device anymore...')
		questions = [
			{
				'type'   : 'list',
				'name'   : 'drive',
				'message': 'Which drive is the SD boot device?',
				'choices': drives
			}
		]
		newAnswers = prompt(questions=questions)
		if not newAnswers:
			commons.returnToMainMenu(ctx, pause=True, message="I'm really sorry, but I just can't continue without this info, sorry for wasting your time...")
		answers = {**answers, **newAnswers}
	else:
		answers['drive'] = drive

	# Now let's enable SSH and Wi-Fi on boot.
	commons.printInfo('Adding ssh & wifi to SD boot....')
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

	commons.returnToMainMenu(ctx, pause=True, message='SD card is ready. Please plug it in your device and boot it!')


def doDownload(url: str, destination: Path):
	with destination.open(mode='wb') as f:
		response = requests.get(url, stream=True)
		size = int(response.headers.get('content-length'))

		with tqdm(total=size, unit='B', unit_scale=True, unit_divisor=1024, desc=url.split('/')[-1], initial=0, ascii=True, miniters=1) as progress:
			for data in response.iter_content(chunk_size=4096):
				f.write(data)
				progress.update(len(data))
