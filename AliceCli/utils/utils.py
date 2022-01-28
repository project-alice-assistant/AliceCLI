#  Copyright (c) 2021
#
#  This file, utils.py, is part of Project Alice CLI.
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
#  Last modified: 2021.03.04 at 17:03:56 CET
#  Last modified by: Psycho

import click
import time
from InquirerPy import inquirer
from InquirerPy.validator import PasswordValidator

from AliceCli.utils import commons
from AliceCli.utils.decorators import checkConnection


@click.command(name='changePassword')
@click.option('-c', '--current_password', type=str, required=True)
@click.option('-p', '--password', type=str, required=True)
@click.pass_context
@checkConnection
def changePassword(ctx: click.Context, current_password: str = None, password: str = None):
	click.secho('Changing password', fg='yellow')

	if not password or not current_password:
		current_password = inquirer.secret(
			message='Enter current password (default: raspberry)',
			default='raspberry',
			transformer=lambda _: commons.HIDDEN,
		).execute()

		retry = True
		while retry:
			password = inquirer.secret(
				message='Enter new password',
				transformer=lambda _: commons.HIDDEN,
				validate=PasswordValidator(length=8, cap=True, number=True, special=False),
			    long_instruction='Password must be at least 8 characters long, contain a number and a capital letter. All this.... for your safety!'
			).execute()
			confirm_password = inquirer.secret(
				message='Confirm new password',
				transformer=lambda _: commons.HIDDEN,
			).execute()

			if password != confirm_password:
				commons.printError('New passwords do not match')
				retry = inquirer.confirm(message='Try again?', default=True).execute()
				if not retry:
					commons.returnToMainMenu(ctx)
					return
			else:
				break

	commons.waitAnimation()
	stdout, stderr = commons.sshCmdWithReturn(f'echo -e "{current_password}\n{password}\n{password}" | passwd')
	error = stderr.readline()
	if 'successfully' in error.lower():
		commons.printSuccess('Password changed!')
	else:
		commons.printError(f'Something went wrong: {error}')

	commons.returnToMainMenu(ctx, pause=True)


@click.command(name='changeHostname')
@click.option('-n', '--hostname', type=str, callback=commons.validateHostname, required=False)
@click.pass_context
@checkConnection
def changeHostname(ctx: click.Context, hostname: str):
	click.secho('Changing device\'s hostname', fg='yellow')

	if not hostname:
		hostname = inquirer.text(
			message='Enter new device name',
			default='ProjectAlice',
			validate=lambda name: commons.validateHostname(name) is not None
		).execute()

	commons.waitAnimation()
	commons.sshCmd(f"sudo hostnamectl set-hostname '{hostname}'")
	ctx.invoke(reboot, ctx, return_to_main_menu=False)

	commons.waitAnimation()
	stdout, stderr = commons.sshCmdWithReturn('hostname')
	if stdout.readline().lower().strip() == hostname.lower().strip():
		commons.printSuccess('Device name changed!')
	else:
		commons.printError('Failed changing device name...')

	commons.returnToMainMenu(ctx, pause=True)


@click.command(name='reboot')
@click.pass_context
@checkConnection
def reboot(ctx: click.Context, return_to_main_menu: bool = True):  # NOSONAR
	click.secho('Rebooting device, please wait', fg='yellow')

	commons.waitAnimation()
	commons.sshCmd('sudo reboot')
	address = commons.CONNECTED_TO
	ctx.invoke(commons.disconnect)
	rebooted = commons.tryReconnect(ctx, address)

	if not rebooted:
		commons.printError('Failed rebooting device')
	else:
		commons.printSuccess('Device rebooted!')

	if return_to_main_menu:
		commons.returnToMainMenu(ctx, pause=True)


@click.command(name='updateSystem')
@click.pass_context
@checkConnection
def updateSystem(ctx: click.Context):
	click.secho('Updating device\'s system, please wait', fg='yellow')

	commons.waitAnimation()
	commons.sshCmd('sudo apt-get update && sudo apt-get upgrade -y')
	commons.printSuccess('Device updated!')
	commons.returnToMainMenu(ctx, pause=True)


@click.command(name='upgradeSystem')
@click.pass_context
@checkConnection
def upgradeSystem(ctx: click.Context):
	click.secho('Upgrading device\'s system, please wait', fg='yellow')

	commons.waitAnimation()
	commons.sshCmd('sudo apt-get update && sudo apt-get dist-upgrade -y')
	commons.printSuccess('Device upgraded!')
	ctx.invoke(reboot)


@click.command(name='soundTest')
@click.pass_context
@checkConnection
def soundTest(ctx: click.Context):
	commons.printInfo('This will test both the recording and playback of your device')
	click.pause('Press enter and read aloud: I am testing my sound input and output')
	commons.printInfo('Now recording...')
	commons.sshCmd('arecord /tmp/test.wav -d 3')
	time.sleep(3.5)
	commons.printInfo('Now playing...')
	commons.sshCmd('aplay /tmp/test.wav')
	time.sleep(3.5)

	confirm = inquirer.confirm(
		message='Did you hear yourself speaking through the device?',
		default=True
	).execute()

	if confirm:
		commons.printSuccess('Great, so both your mic and speakers are working!')
	else:
		commons.printInfo("Ok... Sorry about that... Let's try the audio output only")
		click.pause()
		commons.printInfo('Testing sound output...')
		commons.waitAnimation()
		commons.sshCmd('sudo aplay /usr/share/sounds/alsa/Front_Center.wav')
		commons.stopAnimation()
		confirm = inquirer.confirm(
			message='Ok, I played it and you should have heard the common "front, center" sound test, did you hear it?',
			default=True
		).execute()

		if confirm:
			commons.printInfo("Ok, so this means your audio output is fine, but your mic doesn't capture anything")
			click.pause()
			commons.sshCmd('arecord -l')
			confirm = inquirer.confirm(
				message='Do you see your mic listed in the list above?',
				default=True
			).execute()

			if confirm:
				commons.printInfo('Mmmh, here some potential fixes:\n- Use "alsamixer" to raise the capture volume of your device.\n- Edit your "/etc/asound.conf" to set it up correctly.\n- Try reaching out on our Discord server, maybe others had the same issue?')
			else:
				commons.printInfo('Mmmh, here some potential fixes:\n Edit your "/etc/asound.conf" to set it up correctly.\n- Try reaching out on our Discord server, maybe others had the same issue?')
		else:
			commons.printInfo("Ok, so this would mean the output doesn't work, and maybe the input works, but you can't hear the result...")
			click.pause()
			commons.sshCmd('aplay -l')
			confirm = inquirer.confirm(
				message='Do you see your audio output device listed in the list above?',
				default=True
			).execute()
			if confirm:
				commons.printInfo('Mmmh, here some potential fixes:\n- Use "alsamixer" to raise the output volume of your device.\n- Edit your "/etc/asound.conf" to set it up correctly.\n- Try reaching out on our Discord server, maybe others had the same issue?')
			else:
				commons.printInfo('Mmmh, here some potential fixes:\n Edit your "/etc/asound.conf" to set it up correctly.\n- Try reaching out on our Discord server, maybe others had the same issue?')

	commons.returnToMainMenu(ctx, pause=True)


@click.command(name='systemLogs')
@click.pass_context
@checkConnection
def systemLogs(ctx: click.Context):
	ctx.invoke(displayLogs, file='/var/log/syslog')


@click.command(name='aliceLogs')
@click.pass_context
@checkConnection
def aliceLogs(ctx: click.Context):
	ctx.invoke(displayLogs, file='~/ProjectAlice/var/logs/logs.log')


@click.command(name='logs')
@click.option('-f', '--file', type=str, required=True)
@click.pass_context
@checkConnection
def displayLogs(ctx: click.Context, file: str):
	try:
		commons.sshCmd(f'tail -n 250 -f {file} & {{ read ; kill %1; }}')
	except:
		try:
			commons.SSH.exec_command('\r')
		except:
			address = commons.CONNECTED_TO
			ctx.invoke(commons.disconnect)
			if commons.tryReconnect(ctx, address):
				ctx.invoke(displayLogs, file)
			else:
				commons.printError('Connection to Alice lost')

	commons.returnToMainMenu(ctx)


@click.command(name='disableRespeakerLeds')
@click.pass_context
@checkConnection
def disableRespeakerLeds(ctx: click.Context):
	click.echo('Turning off Respeaker always on leds')
	commons.waitAnimation()
	click.echo('Make sure we have pip')
	commons.sshCmd('sudo apt-get install python3-pip -y')
	click.echo('Install pixel ring our savior')
	commons.sshCmd('sudo pip3 install pixel_ring')  # sudo is required here, that's bad, but we uninstall directly after
	click.echo('Testing the leds and turning off')
	commons.sshCmd('pixel_ring_check', hide=True)
	time.sleep(3)
	click.echo('Uninstall pixel ring as we don\'t need it anymore')
	commons.sshCmd('sudo pip3 uninstall pixel_ring -y')
	commons.stopAnimation()
	commons.printSuccess('Should be done!')
	commons.returnToMainMenu(ctx, pause=True)
