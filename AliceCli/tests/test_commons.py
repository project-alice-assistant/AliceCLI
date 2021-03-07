from unittest import TestCase

import click

from AliceCli.utils import commons


class Test_Commons(TestCase):

	def test_discover(self):
		pass # Nothing to test


	def test_connect(self):
		pass # Nothing to test


	def test_print_error(self):
		pass # Nothing to test


	def test_print_success(self):
		pass # Nothing to test


	def test_print_info(self):
		pass # Nothing to test


	def test_disconnect(self):
		pass # Nothing to test


	def test_wait_animation(self):
		pass # Nothing to test


	def test_ctrl_cexplained(self):
		pass # Nothing to test


	def test_stop_animation(self):
		pass # Nothing to test


	def test__animation(self):
		pass # Nothing to test


	def test__ctrl_cexplained(self):
		pass # Nothing to test


	def test_ask_return_to_main_menu(self):
		pass # Nothing to test


	def test_return_to_main_menu(self):
		pass # Nothing to test


	def test_validate_hostname(self):
		self.assertRaises(TypeError, commons.validateHostname)
		self.assertRaises(click.BadParameter, commons.validateHostname, '')
		self.assertRaises(click.BadParameter, commons.validateHostname, 'a' * 255)
		self.assertRaises(click.BadParameter, commons.validateHostname, 'project alice')
		self.assertRaises(click.BadParameter, commons.validateHostname, 'project?alice')
		self.assertEqual(commons.validateHostname('ProjectAlice'), 'ProjectAlice')
