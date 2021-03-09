[![Upload Python Package](https://github.com/project-alice-assistant/AliceCLI/actions/workflows/python-publish.yml/badge.svg)](https://github.com/project-alice-assistant/AliceCLI/actions/workflows/python-publish.yml)
 [![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=project-alice-assistant_AliceCLI&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=project-alice-assistant_AliceCLI)
 [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=project-alice-assistant_AliceCLI&metric=alert_status)](https://sonarcloud.io/dashboard?id=project-alice-assistant_AliceCLI)
 [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=project-alice-assistant_AliceCLI&metric=coverage)](https://sonarcloud.io/dashboard?id=project-alice-assistant_AliceCLI) 

# Project Alice CLI

This is a Project Alice command line tool.

It simplifies to the maximum the installation and maintenance of Project Alice.

It is not meant to be installed on the device that runs/will run Alice, but on your main computer.

It handles connecting to network discoverable devices through SSH and generates RSA keys for a passwordless connection.

Although it's a command line tool, made possible thanks to the awesome "Click" package, it is using the wonderful "PyInquirer" package to offer an interactive menu for people not used or wanting to type commands.

# Users
Install this tool via pip, on your main computer:

`pip3 install projectalice-cli`

Note that you need Python 3.8 at least


# Devs of this tool
- Clone this repository
- Open a terminal on whatever OS you are
- CD to the path where you cloned this repository
- Create a python 3.8+ virtual environement:
  `python -m venv`
- Activate your virtual environement
- Install the package in dev mode:
  `pip install --editable .`
  
# Usage
Type `alice` in your terminal to open the main menu or type `alice --help` to discover the available commands

# Useful information
This tool stores its configurations in `%USER_DIRECTORY%/.pacli`

This tool stores its generated SSH certificates in `%USER_DIRECTORY%/.ssh`
