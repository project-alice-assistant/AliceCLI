#  Copyright (c) 2021
#
#  This file, test_commons.py, is part of Project Alice CLI.
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
#  Last modified: 2021.03.07 at 13:37:37 CET
#  Last modified by: Psycho

from unittest import TestCase

import click

from AliceCli.utils import commons


class Test_Commons(TestCase):

	def test_discover(self):
		pass  # Nothing to test


	def test_connect(self):
		pass  # Nothing to test


	def test_print_error(self):
		pass  # Nothing to test


	def test_print_success(self):
		pass  # Nothing to test


	def test_print_info(self):
		pass  # Nothing to test


	def test_disconnect(self):
		pass  # Nothing to test


	def test_wait_animation(self):
		pass  # Nothing to test


	def test_ctrl_cexplained(self):
		pass  # Nothing to test


	def test_stop_animation(self):
		pass  # Nothing to test


	def test__animation(self):
		pass  # Nothing to test


	def test__ctrl_cexplained(self):
		pass  # Nothing to test


	def test_ask_return_to_main_menu(self):
		pass  # Nothing to test


	def test_return_to_main_menu(self):
		pass  # Nothing to test


	def test_validate_hostname(self):
		self.assertRaises(TypeError, commons.validateHostname)
		self.assertRaises(click.BadParameter, commons.validateHostname, '')
		self.assertRaises(click.BadParameter, commons.validateHostname, 'a' * 255)
		self.assertRaises(click.BadParameter, commons.validateHostname, 'project alice')
		self.assertRaises(click.BadParameter, commons.validateHostname, 'project?alice')
		self.assertEqual(commons.validateHostname('ProjectAlice'), 'ProjectAlice')
