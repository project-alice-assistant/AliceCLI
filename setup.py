#  Copyright (c) 2021
#
#  This file, setup.py, is part of Project Alice CLI.
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
#  Last modified: 2021.04.13 at 14:40:14 CEST
#  Last modified by: Psycho

from pathlib import Path

from setuptools import find_packages, setup


setup(
	name='projectalice-cli',
	version='0.2.5',
	long_description=Path('README.md').read_text(encoding='utf8'),
	long_description_content_type='text/markdown',
	python_requires='>=3.8',
	packages=find_packages(),
	include_package_data=True,
	url='https://github.com/project-alice-assistant/AliceCLI',
	license='GPL-3.0',
	author='ProjectAlice',
	maintainer='Psychokiller1888',
	author_email='laurentchervet@bluewin.ch',
	description='Project Alice CLI tool',
	install_requires=[
		'click~=8.0.3',
		'paramiko~=2.8.1',
		'PyInquirer~=1.0.3',
		'networkscan~=1.0.9',
		'pyyaml~=6.0',
		'requests~=2.26.0',
		'psutil~=5.8.0',
		'beautifulsoup4~=4.10.0',
		'tqdm~=4.62.3',
		'pytest~=6.2.5',
		'coverage~=6.2',
		'pytest-cov~=3.0.0',
		'coveralls~=3.3.1'
    ],
	classifiers=[
		"Development Status :: 4 - Beta",
		"Environment :: Console",
		"Intended Audience :: End Users/Desktop",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Operating System :: OS Independent",
		"Programming Language :: Python :: 3.8",
		"Topic :: Home Automation",
		"Topic :: System :: Installation/Setup"
	],
    entry_points='''
        [console_scripts]
        alice=AliceCli.AliceCli:cli
    '''
)
