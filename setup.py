from pathlib import Path

from setuptools import find_packages, setup


setup(
	name='projectalice-cli',
	version='0.0.1',
	long_description=Path('README.md').read_text(encoding='utf8'),
	long_description_content_type='text/markdown',
	packages=find_packages(),
	include_package_data=True,
	url='https://github.com/project-alice-assistant/AliceCLI',
	license='GPL-3.0',
	author='Psychokiller1888',
	author_email='laurentchervet@bluewin.ch',
	description='Project Alice CLI tool',
	install_requires=[
        'Click',
		'paramiko',
		'PyInquirer'
    ],
	classifiers=[
		"Development Status :: 2 - Pre-Alpha",
		"Environment :: Console",
		"Intended Audience :: End Users/Desktop",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Operating System :: OS Independent",
		"Programming Language :: Python :: 3.7",
		"Topic :: Home Automation",
		"Topic :: System :: Installation/Setup"
	],
    entry_points='''
        [console_scripts]
        alice=AliceCli.AliceCli:cli
    '''
)
