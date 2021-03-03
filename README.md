# Project Alice CLI

This is a Project Alice command line tool.

It simplifies to the maximum the installation and maintenance of Project Alice.

It is not meant to be installed on the device that runs/will run Alice, but on your main computer.

It handles connecting to network discoverable devices through SSH and generates RSA keys for a passwordless connection.

Although it's a command line tool, it is using the wonderful "Click" package to offer an interactive menu for people not used or wanting to type commands.

# Users
Install this tool via pip, on your main computer:

`pip3 install projectalice-cli`


# Devs of this tool
- Clone this repository
- Open a terminal on whatever OS you are
- CD to the path where you cloned this repository
- Create a python 3.7+ virtual environement:
  `python -m venv`
- Activate your virtual environement
- Install the package in dev mode:
  `pip install --editable .`
  
# Usage
Type `alice` in your terminal to open the main menu or type `alice --help` to discover the available commands

# Useful information
This tool stores its configurations in `%USER_DIRECTORY%/.pacli`
This tool stores its generated SSH certificates in `%USER_DIRECTORY%/.ssh`
