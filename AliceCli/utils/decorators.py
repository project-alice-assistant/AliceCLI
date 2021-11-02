#  Copyright (c) 2021
#
#  This file, decorators.py, is part of Project Alice CLI.
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
#  Last modified: 2021.03.04 at 14:54:39 CET
#  Last modified by: Psycho

import AliceCli.utils.commons as commons


def checkConnection(func):
	def wrapper(*args, **kwargs):
		if not commons.SSH:
			commons.printError('Please connect to a server first')
			args[0].invoke(commons.discover, return_to_main_menu=False)

		func(args[0], **kwargs)


	return wrapper
