#  Copyright (c) 2021
#
#  This file, alice.py, is part of Project Alice CLI.
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
#  Last modified: 2021.03.03 at 13:15:43 CET
#  Last modified by: Psycho

import click

from AliceCli.utils import commons
from AliceCli.utils.decorators import checkConnection


@click.command(name='updateAlice')
@click.pass_context
@checkConnection
def updateAlice(ctx: click.Context):
	click.secho('Updating Alice, please wait', color='yellow')

	commons.waitAnimation()
	commons.SSH.exec_command('sudo systemctl stop ProjectAlice')
	stdin, stdout, stderr = commons.SSH.exec_command('cd ~/ProjectAlice && git pull && git submodules foreach git pull')
	line = stdout.readline()
	while line:
		click.secho(line, nl=False, color='yellow')
		line = stdout.readline()

	commons.SSH.exec_command('sudo systemctl start ProjectAlice')
	commons.printSuccess('Alice updated!')
	commons.returnToMainMenu(ctx, pause=True)


@click.command(name='do')
@click.option('-o', '--option', required=True, type=click.Choice(['start', 'stop', 'restart', 'enable', 'disable', 'status'], case_sensitive=False))
@click.pass_context
@checkConnection
def systemctl(ctx: click.Context, option: str):
	click.secho(f'Service "{option}", please wait', color='yellow')

	commons.waitAnimation()
	stdin, stdout, stderr = commons.SSH.exec_command(f'sudo systemctl {option} ProjectAlice')
	line = stdout.readline()
	while line:
		click.secho(line, nl=False, color='yellow')
		line = stdout.readline()

	commons.printSuccess('Done!')
	commons.returnToMainMenu(ctx, pause=True)


@click.command(name='reportBug')
@click.pass_context
@checkConnection
def reportBug(ctx: click.Context):
	click.secho('Enabling inbuilt bug reporter', color='yellow')

	commons.waitAnimation()
	commons.SSH.exec_command('touch ~/ProjectAlice/alice.bugreport')
	click.secho('Restarting Alice', color='yellow')
	commons.SSH.exec_command('sudo systemctl restart ProjectAlice')

	commons.printSuccess('Bug reporter enabled and Alice restart. As soon as a fatal error occurs and/or she is stopped, the session report will be posted to Github!')
	commons.returnToMainMenu(ctx, pause=True)
