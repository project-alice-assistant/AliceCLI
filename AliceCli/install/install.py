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
import click
import json
import os
import platform
import psutil
import requests
import subprocess
import tempfile
import time
import yaml
import zipfile
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.validator import EmptyInputValidator, PathValidator
from pathlib import Path
from shutil import which
from tqdm import tqdm
from typing import List

from AliceCli.utils import commons
from AliceCli.utils.commons import sshCmd, sshCmdWithReturn
from AliceCli.utils.decorators import checkConnection
from AliceCli.utils.utils import reboot, systemLogs


@click.command(name='installSoundDevice')
@click.option('-d', '--device', type=click.Choice(['respeaker2', 'respeaker4', 'respeaker4MicLinearArray', 'respeaker6MicArray'], case_sensitive=False))
@click.pass_context
@checkConnection
def installSoundDevice(ctx: click.Context, device: str):
	click.secho('Installing audio hardware', fg='yellow')
	commons.waitAnimation()
	if not device:
		device = getDeviceName()
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


@click.command(name='uninstallSoundDevice')
@click.option('-d', '--device', type=click.Choice(['respeaker2', 'respeaker4', 'respeaker4MicLinearArray', 'respeaker6MicArray'], case_sensitive=False))
@click.pass_context
@checkConnection
def uninstallSoundDevice(ctx: click.Context, device: str, return_to_main_menu: bool = True):  # NOSONAR
	click.secho('Uninstalling audio hardware', fg='yellow')
	commons.waitAnimation()
	if not device:
		device = getDeviceName()
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


def getDeviceName() -> str:
	return inquirer.select(
		message='Select your device',
		choices=[
			Choice('respeaker2', name='Respeaker 2'),
			Choice('respeaker4', name='Respeaker 4-mic array'),
			Choice('respeaker4MicLinearArray', name='Respeaker 4 mic linear array'),
			Choice('respeaker6MicArray', name='Respeaker 6 mic array')
		]
	).execute()


def install(ctx: click.Context, force: bool, name: str):
	click.secho(f'\nInstalling {name}!', fg='yellow')

	result = sshCmdWithReturn('test -d ~/ProjectAlice/ && echo "1"')[0].readline()
	if result:
		if not force:
			commons.printError('Alice seems to already exist on that host')
			confirm = inquirer.confirm(
				message='Erase and reinstall?',
				default=False
			).execute()

			if not confirm:
				commons.returnToMainMenu(ctx)
				return

		sshCmd('sudo systemctl stop ProjectAlice')
		sshCmd('sudo rm -rf ~/ProjectAlice')

	releaseType = inquirer.select(
		message='What releases do you want to receive? If you are unsure, leave this to Stable releases!',
		default='master',
		choices=[
			Choice('master', name='Stable releases'),
			Choice('rc', name='Release candidates'),
			Choice('beta', name='Beta releases'),
			Choice('alpha', name='Alpha releases')
		]
	).execute()

	confFile = Path(Path.home(), f'.pacli/{name}.yaml')
	confFile.parent.mkdir(parents=True, exist_ok=True)

	updateSource = commons.getUpdateSource(name, releaseType)

	try:
		with requests.get(url=f'https://raw.githubusercontent.com/project-alice-assistant/{name}/{updateSource}/{name}.yaml', stream=True) as r:
			r.raise_for_status()
			with confFile.open('wb') as fp:
				for chunk in r.iter_content(chunk_size=8192):
					if chunk:
						fp.write(chunk)
	except Exception as e:
		commons.printError(f'Failed downloading {name}.yaml {e}')
		commons.returnToMainMenu(ctx, pause=True)

	with confFile.open(mode='r') as f:
		try:
			config = yaml.safe_load(f)
		except yaml.YAMLError as e:
			commons.printError(f'Failed reading {name}.yaml {e}')
			commons.returnToMainMenu(ctx, pause=True)

	if name == 'ProjectAlice':
		config = getAliceConfig(config, releaseType)
	elif name == 'ProjectAliceSatellite':
		config = getAliceSatConfig(config, releaseType)
	else:
		commons.printError(f'Unknown install type {name}')

	commons.waitAnimation()
	with confFile.open(mode='w') as f:
		yaml.dump(config, f)

	commons.printSuccess(f'Generated {name}.yaml')

	commons.printInfo('Updating system')
	sshCmd('sudo apt-get update')
	sshCmd('sudo apt-get install git -y')
	sshCmd('git config --global user.name "Han Oter"')
	sshCmd('git config --global user.email "anotheruser@projectalice.io"')

	commons.printInfo('Cloning Alice')
	sshCmd(f'git clone https://github.com/project-alice-assistant/{name}.git ~/ProjectAlice')
	if name == 'ProjectAliceSatellite':
		sshCmd(f'git checkout 1.0.0-rc1')
		sshCmd(f'git pull')

	sftp = commons.SSH.open_sftp()
	sftp.put(str(confFile), f'/home/pi/ProjectAlice/{name}.yaml')
	sftp.close()

	sshCmd(f'sudo rm /boot/{name}.yaml')
	sshCmd(f'sudo cp ~/ProjectAlice/{name}.yaml /boot/{name}.yaml')

	commons.printInfo('Start install process')
	sshCmd('cd ~/ProjectAlice/ && python3 main.py')

	commons.printSuccess('Alice has completed the basic installation! She\'s now working further to complete the installation, let\'s see what she does!')
	ctx.invoke(systemLogs)


@click.command(name='installAlice')
@click.option('--force', '-f', is_flag=True)
@click.pass_context
@checkConnection
def installAlice(ctx: click.Context, force: bool):
	install(ctx, force, 'ProjectAlice')


@click.command(name='installAliceSatellite')
@click.option('--force', '-f', is_flag=True)
@click.pass_context
@checkConnection
def installAliceSatellite(ctx: click.Context, force: bool):
	install(ctx, force, 'ProjectAliceSatellite')


@click.command(name='prepareSdCard')
@click.pass_context
def prepareSdCard(ctx: click.Context):  # NOSONAR
	if not commons.isAdmin():
		commons.returnToMainMenu(ctx=ctx, pause=True, message='You need admin rights for this, please restart Alice CLI with admin elevated rights.')
		return

	operatingSystem = platform.system().lower()

	balenaExecutablePath = getBalenaPath()
	flasherAvailable = balenaExecutablePath != None

	downloadsPath = Path.home() / 'Downloads'

	doFlash = inquirer.confirm(
		message='Do you want to flash your SD card with Raspberry PI OS?',
		default=False
	).execute()

	installBalena = False
	if not flasherAvailable:
		installBalena = inquirer.confirm(
			message='balena-cli was not found on your system. It is required for working with SD cards, do you want to install it?',
			default=True
		)

	if not flasherAvailable and not installBalena:
		commons.returnToMainMenu(ctx, pause=True, message='Well then, I cannot work with your SD card without the appropriate tool to do it')
		return
	elif not flasherAvailable and installBalena:
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
			commons.printInfo('Downloading...')
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
			commons.printInfo('Setting ./balena-cli/balena as executable...')
			# set executable permission
			# from https://stackoverflow.com/questions/12791997/how-do-you-do-a-simple-chmod-x-from-within-python
			executablePath.chmod(509)  # now shell `./balena-cli/balena version` works
			commons.printInfo('Adding ./balena-cli to PATH...')
			os.environ['PATH'] += os.pathsep + str(executablePath.parent)
			sysPath = os.environ['PATH']
			commons.printInfo(f'New PATH: {sysPath}')
			click.pause('Installation Done. Press a key')
		elif operatingSystem == 'darwin':
			subprocess.run(f'sudo installer -pkg {destination} -target /', shell=True)
			click.pause('Installation Done. Press a key')
		else:
			click.pause(f'I have no idea how to install stuff on {operatingSystem}. Please install balena manually. Oh, and contact us on discord to let us know how to install it ;)')
			exit(0)

	if doFlash:
		images = list()
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
		drives = list()

		sdCards = getSdCards()
		for sdCard in sdCards:
			drives.append(Choice(sdCard, name=sdCard))

		if not drives:
			commons.returnToMainMenu(ctx, pause=True, message='Please insert your SD card first')
			return

		image = inquirer.select(
			message='Select the image you want to flash. Keep in mind we only officially support the "Buster" Raspberry pi OS distro!',
			choices=images
		).execute()

		drive = inquirer.select(
			message='Select your SD card drive',
			choices=drives
		).execute()

		commons.printInfo("Flashing SD card, please wait")

		if image.startswith('https'):
			file = downloadsPath / image.split('/')[-1]
			doDownload(url=image, destination=file)
		else:
			file = image

		if operatingSystem == 'windows' or operatingSystem == 'linux' or operatingSystem == 'darwin':
			if operatingSystem == 'linux' or operatingSystem == 'darwin':
				# this only works on distros with "sudo" support.
				balenaCommand = f'sudo {balenaExecutablePath} local flash {str(file)} --drive {drive} --yes'
			else:
				balenaCommand = f'balena local flash {str(file)} --drive {drive} --yes'.split()
			subprocess.run(balenaCommand, shell=True)
			time.sleep(5)
		else:
			commons.returnToMainMenu(ctx, pause=True, message='Flashing only supported on Windows, Linux and MacOs systems for now. If you have the knowledge to implement it on other systems, feel free to pull request!')
			return

		click.pause('Flashing complete. Please eject, unplug and replug your SD back, then press any key to continue...')

	ssid = inquirer.text(
		message='Enter the name of your Wifi network',
		validate=EmptyInputValidator(commons.NO_EMPTY)
	).execute()

	password = inquirer.secret(
		message='Enter your Wifi network\'s key',
		transformer=lambda _: commons.HIDDEN
	).execute()

	country = inquirer.select(
		message='Select your country. This is used for your Wi-Fi settings!',
		default='EN',
		choices=commons.COUNTRY_CODES
	).execute()

	drives = list()
	drive = ''
	if operatingSystem == 'linux':
		# typically, boot partition is the first increment of SD device
		# e.g. on /dev/sda drive /dev/sda1 is "boot" and /dev/sda2 is "rootfs"
		# Lookup up the boot mount point path via lsblk

		sdCards = getSdCards()
		command = f'sudo lsblk -o PATH,FSTYPE,LABEL,MOUNTPOINT --json'

		output = subprocess.run(command, capture_output=True, shell=True).stdout.decode()
		blkDevices = json.loads(output)

		for device in blkDevices['blockdevices']:
			if device["path"].startswith(tuple(sdCards)) and device['fstype'] == 'vfat' and device['label'] == 'boot':
				drives.append(Choice(value=device, name=device['path']))

	elif operatingSystem == 'darwin':
		sdCards = getSdCards()
		sdCards = [sd.split('/')[-1] for sd in sdCards]

		command = f'diskutil list -plist | plutil -convert json -r -o - -'

		output = subprocess.run(command, capture_output=True, shell=True).stdout.decode()
		allDevices = json.loads(output)

		for device in allDevices['AllDisksAndPartitions']:
			if device["DeviceIdentifier"].startswith(tuple(sdCards)):
				commons.printInfo(f'Checking partitions of {device["DeviceIdentifier"]}')
				for part in device['Partitions']:
					commons.printInfo(f'{part}')
					if 'Content' in part and part['Content'] == 'Windows_FAT_32' and 'VolumeName' in part and part['VolumeName'] == 'boot':
						drives.append(Choice(value=part['MountPoint'], name=device['DeviceIdentifier']))
			else:
				commons.printInfo(f'Device not relevant: {device["DeviceIdentifier"]}')

	else:
		j = 0
		while len(drives) <= 0:
			j += 1
			for dp in psutil.disk_partitions():
				if 'rw,removable' not in dp.opts.lower():
					continue

				drives.append(dp.device)

			if not drives:
				if j < 3:
					drives = list()
					commons.printError('For some reason I cannot find any writable SD partition. Please eject then unplug, replug your SD back and press any key to continue')
					click.pause()
				else:
					break

	if len(drives) == 0:
		commons.printError(f'For some reason I cannot find the SD boot partition mount point {drive}.')
		commons.returnToMainMenu(ctx, pause=True, message="I'm really sorry, but I just can't continue without this info, sorry for wasting your time...")

	if len(drives) == 1:
		try:
			device = drives[0].value
		except:
			device = drives[0]

		if operatingSystem == 'linux':
			commons.printInfo(f'Auto-selected {device["path"]}.')
		else:
			commons.printInfo(f'Auto-selected {device}.')
		drive = device

	if not drive:
		drive = inquirer.select(
			message='Please select the correct SD `boot` partition',
			choices=drives
		).execute()

	needToUnmount = False
	mountDir = ''
	if operatingSystem == 'linux':
		# if device has not been mounted yet, mount in temp directory
		if drive['mountpoint'] is None:
			needToUnmount = True
			mountDir = tempfile.mkdtemp(prefix='alice-cli-mount-')
			command = f"sudo mount {drive['path']} {mountDir}"
			result = subprocess.run(command, capture_output=True, shell=True)
			if not result.returncode == 0:
				commons.printError(f"Could not mount {drive['path']} to {mountDir}.")
				commons.returnToMainMenu(ctx, pause=True)
			drive['mountpoint'] = mountDir
			commons.printInfo(f"Mounted {drive['path']} to {mountDir} temporarily.")
		else:
			commons.printInfo(f"{drive['path']} is already mounted to {drive['mountpoint']}.")
		drive = drive['mountpoint']

	# Now let's enable SSH and Wi-Fi on boot.
	commons.printInfo('Adding ssh & wifi to SD boot....')
	sshFile = Path(drive, 'ssh')
	sshFile.unlink(missing_ok=True)
	sshFile.touch()

	content = f'country={country}\n'
	content += 'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n'
	content += 'update_config=1\n'
	content += 'network={\n'
	content += f'\tssid="{ssid}"\n'
	content += '\tscan_ssid=1\n'
	content += f'\tpsk="{password}"\n'
	content += '\tkey_mgmt=WPA-PSK\n'
	content += '}'
	Path(drive, 'wpa_supplicant.conf').write_text(content)

	if operatingSystem == 'linux' and needToUnmount and mountDir:
		command = f'sudo umount {drive}'
		result = subprocess.run(command, capture_output=True, shell=True)
		if not result.returncode == 0:
			commons.printError(f'Could not unmount {drive}.')
			commons.returnToMainMenu(ctx, pause=True)
		commons.printInfo(f'Unmounted {drive}')
		# only deletes empty dirs, so if unmounting failed for whatever reasons, we don't destroy anything
		os.rmdir(mountDir)

	commons.returnToMainMenu(ctx, pause=True, message='SD card is ready. Please plug it in your device and boot it!')


def doDownload(url: str, destination: Path):
	os.makedirs(os.path.dirname(destination), exist_ok = True)
	with destination.open(mode='wb') as f:
		response = requests.get(url, stream=True)
		size = int(response.headers.get('content-length'))

		with tqdm(total=size, unit='B', unit_scale=True, unit_divisor=1024, desc=url.split('/')[-1], initial=0, ascii=True, miniters=1) as progress:
			for data in response.iter_content(chunk_size=4096):
				f.write(data)
				progress.update(len(data))


def getSdCards() -> List[str]:
	operatingSystem = platform.system().lower()
	if operatingSystem == 'windows':
		balenaCommand = 'balena util available-drives'
		driveSep = '\\'
	else:
		balenaExecutablePath = getBalenaPath()
		balenaCommand = f'{balenaExecutablePath} util available-drives'
		driveSep = os.path.sep  # typically '/'

	drives = list()

	output = subprocess.run(balenaCommand, capture_output=True, shell=True).stdout.decode()
	for line in output.split('\n'):
		if not line.startswith(driveSep):
			continue
		drives.append(line.split()[0])

	return drives


def getBalenaPath() -> str:
	operatingSystem = platform.system().lower()
	balenaExecutablePath = which('balena')
	if not balenaExecutablePath and operatingSystem == 'linux':
		balenaExecutablePath = str(Path.joinpath(Path.cwd(), 'balena-cli', 'balena'))  # default install path

	return balenaExecutablePath


def getAliceConfig(confs, releaseType):
	adminPinCode = inquirer.secret(
			message='Enter an admin pin code. It must be made of 4 characters, all digits only. (default: 1234)',
			default='1234',
			validate=lambda code: code.isdigit() and int(code) < 10000,
			invalid_message='Pin must be 4 numbers',
			transformer=lambda _: commons.HIDDEN
	).execute()

	mqttHost = inquirer.text(
			message='Mqtt hostname',
			default='localhost',
			validate=EmptyInputValidator(commons.NO_EMPTY)
	).execute()

	mqttPort = inquirer.text(
			message='Mqtt port',
			default='1883',
			validate=EmptyInputValidator(commons.NO_EMPTY)
	).execute()

	activeLanguage = inquirer.select(
			message='What language should Alice be using?',
			default='en',
			choices=[
				Choice('en', name='English'),
				Choice('de', name='German'),
				Choice('fr', name='French'),
				Choice('it', name='Italian'),
				Choice('pl', name='Polish'),
			]
	).execute()

	activeCountryCode = inquirer.select(
			message='Enter the country code to use.',
			default='EN',
			choices=commons.COUNTRY_CODES
	).execute()

	audioDevice = inquireAudioDevice()

	soundInstalled = inquirer.confirm(
			message='Did you already install your sound hardware using Alice CLI or confirmed it to be working?',
			default=False
	).execute()

	installHLC = inquirer.confirm(
			message='Do you want to install HLC? HLC can pilot leds such as the ones on Respeakers to provide visual feedback.',
			default=False
	).execute()

	advancedConfigs = inquirer.confirm(
			message='Do you want to set more advanced configs? If you do, DO NOT ABORT IN THE MIDDLE!',
			default=False
	).execute()

	asr = 'coqui'
	tts = 'pico'
	awsAccessKey = ''
	awsSecretKey = ''
	googleServiceFile = ''
	shortReplies = False
	devMode = False
	githubUsername = ''
	githubToken = ''
	enableDataStoring = True
	skillAutoUpdate = True

	if advancedConfigs:
		asr = inquirer.select(
				message='Select the ASR engine you want to use',
				default='coqui',
				choices=[
					Choice('coqui', name='Coqui'),
					Choice('snips', name='Snips (/!\ English only)'),
					Choice('google', name='Google (/!\ Online)'),
					Choice('deepspeech', name='Deepspeech'),
					Choice('pocketsphinx', name='PocketSphinx')
				]
		).execute()

		tts = inquirer.select(
				message='Select the TTS engine you want to use',
				default='pico',
				choices=[
					Choice('pico', name='Coqui'),
					Choice('mycroft', name='Mycroft'),
					Choice('amazon', name='Amazon (/!\ Online)'),
					Choice('google', name='Google (/!\ Online)'),
					Choice('watson', name='Watson (/!\ Online)')
				]
		).execute()

		if tts == 'amazon':
			awsAccessKey = inquirer.secret(
					message='Enter your AWS access key',
					validate=EmptyInputValidator(commons.NO_EMPTY),
					transformer=lambda _: commons.HIDDEN
			).execute()

			awsSecretKey = inquirer.secret(
					message='Enter your AWS secret key',
					validate=EmptyInputValidator(commons.NO_EMPTY),
					transformer=lambda _: commons.HIDDEN
			).execute()

		if tts == 'google' or asr == 'google':
			googleServiceFile = inquirer.filepath(
					message='Enter your Google service file path',
					default='',
					validate=PathValidator(is_file=True, message='Input is not a file')
			).execute()

		shortReplies = inquirer.confirm(
				message='Do you want Alice to use short replies?',
				default=False
		).execute()

		devMode = inquirer.confirm(
				message='Do you want to activate the developer mode?',
				default=False
		).execute()

		if devMode:
			githubUsername = inquirer.text(
					message='Enter your Github username. This is required for Dev Mode.',
					validate=EmptyInputValidator(commons.NO_EMPTY)
			).execute()

			githubToken = inquirer.secret(
					message='Enter your Github access token. This is required for Dev Mode.',
					validate=EmptyInputValidator(commons.NO_EMPTY),
					transformer=lambda _: commons.HIDDEN
			).execute()

		enableDataStoring = inquirer.confirm(
				message='Enable telemetry data storing?',
				default=True
		).execute()

		skillAutoUpdate = inquirer.confirm(
				message='Enable skill auto update?',
				default=True
		).execute()

	confs['adminPinCode'] = str(int(adminPinCode)).zfill(4)
	confs['mqttHost'] = mqttHost
	confs['mqttPort'] = int(mqttPort)
	confs['activeLanguage'] = activeLanguage
	confs['activeCountryCode'] = activeCountryCode
	confs['useHLC'] = installHLC
	confs['aliceUpdateChannel'] = releaseType
	confs['skillsUpdateChannel'] = releaseType
	confs['ttsLanguage'] = f'{activeLanguage}-{activeCountryCode}'

	if soundInstalled:
		confs['installSound'] = False
	else:
		confs['installSound'] = True

	if audioDevice:
		confs['audioHardware'][audioDevice] = True

	confs['asr'] = asr
	confs['awsAccessKey'] = awsAccessKey
	confs['awsSecretKey'] = awsSecretKey
	confs['tts'] = tts
	confs['shortReplies'] = shortReplies
	confs['devMode'] = devMode
	confs['githubUsername'] = githubUsername
	confs['githubToken'] = githubToken
	confs['enableDataStoring'] = enableDataStoring
	confs['skillAutoUpdate'] = skillAutoUpdate

	if googleServiceFile and Path(googleServiceFile).exists():
		confs['googleServiceFile'] = Path(googleServiceFile).read_text()

	if asr == 'google':
		confs['keepASROffline'] = False

	if tts in ['amazon', 'google', 'watson']:
		confs['keepTTSOffline'] = False

	return confs


def getAliceSatConfig(confs, releaseType):
	audioDevice = inquireAudioDevice()

	soundInstalled = inquirer.confirm(
			message='Did you already install your sound hardware using Alice CLI or confirmed it to be working?',
			default=False
	).execute()

	installHLC = inquirer.confirm(
			message='Do you want to install HLC? HLC can pilot leds such as the ones on Respeakers to provide visual feedback.',
			default=False
	).execute()

	confs['useHLC'] = installHLC
	confs['aliceUpdateChannel'] = releaseType

	if soundInstalled:
		confs['installSound'] = False
	else:
		confs['installSound'] = True

	if audioDevice:
		confs['audioHardware'][audioDevice] = True

	return confs


def inquireAudioDevice():
	return inquirer.select(
			message='Select your audio hardware if listed',
			default='respeaker2',
			choices=[
				Choice('respeaker2', name='Respeaker 2 mics'),
				Choice('respeaker4', name='Respeaker 4 mic array'),
				Choice('respeaker4MicLinear', name='Respeaker 4 mic linear array'),
				Choice('respeaker6', name='Respeaker 6 mic array'),
				Choice('respeaker7', name='Respeaker 7'),
				Choice('respeakerCoreV2', name='Respeaker Core version 2'),
				Choice('googleAIY', name='Google AIY'),
				Choice('googleAIY2', name='Google AIY 2'),
				Choice('matrixCreator', name='Matrix Creator'),
				Choice('matrixVoice', name='Matrix Voice'),
				Choice('ps3eye', name='PS3 Eye'),
				Choice('jabra410', name='Jabra 410'),
				Choice(None)
			]
	).execute()
