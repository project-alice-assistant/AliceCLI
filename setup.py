from pathlib import Path

from setuptools import find_packages, setup


setup(
	name='projectalice-cli',
	version='0.1.1',
	long_description=Path('README.md').read_text(encoding='utf8'),
	long_description_content_type='text/markdown',
	python_requires = '>=3.8',
	packages=find_packages(),
	include_package_data=True,
	url='https://github.com/project-alice-assistant/AliceCLI',
	license='GPL-3.0',
	author='ProjectAlice',
	maintainer='Psychokiller1888',
	author_email='laurentchervet@bluewin.ch',
	description='Project Alice CLI tool',
	install_requires=[
        'Click',
		'paramiko',
		'PyInquirer',
		'networkscan',
		'pyyaml',
		'requests',
		'psutil'
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
