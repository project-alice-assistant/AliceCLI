#  Copyright (c) 2021
#
#  This file, commons.py, is part of Project Alice CLI.
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
#  Last modified: 2021.03.07 at 13:31:43 CET
#  Last modified by: Psycho
import click
import ctypes
import json
import os
import paramiko
import re
import requests
import socket
import sys
import time
import uuid
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from networkscan import networkscan
from pathlib import Path
from threading import Event, Thread
from typing import Optional, Tuple

from AliceCli.Version import Version


IP_REGEX = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
SSH: Optional[paramiko.SSHClient] = None
CONNECTED_TO: str = ''
ANIMATION_FLAG = Event()
ANIMATION_THREAD: Optional[Thread] = None
HIDDEN = '[hidden]'
NO_EMPTY = 'Cannot be empty'
COUNTRY_CODES = [
	Choice('CH', name='Switzerland'),
	Choice('DE', name='Germany'),
	Choice('US', name='United States of America (the)'),
	Choice('AU', name='Australia'),
	Choice('GB', name='United Kingdom of Great Britain and Northern Ireland (the)'),
	Choice('FR', name='France'),
	Choice('IT', name='Italy'),
	Choice('PL', name='Poland'),
	Choice('PT', name='Portugal'),
	Choice('BR', name='Brazil'),
	Separator(),
	Choice('AF', name='Afghanistan'),
	Choice('AL', name='Albania'),
	Choice('DZ', name='Algeria'),
	Choice('AS', name='American Samoa'),
	Choice('AD', name='Andorra'),
	Choice('AO', name='Angola'),
	Choice('AI', name='Anguilla'),
	Choice('AQ', name='Antarctica'),
	Choice('AG', name='Antigua and Barbuda'),
	Choice('AR', name='Argentina'),
	Choice('AM', name='Armenia'),
	Choice('AW', name='Aruba'),
	Choice('AT', name='Austria'),
	Choice('AZ', name='Azerbaijan'),
	Choice('BS', name='Bahamas (the)'),
	Choice('BH', name='Bahrain'),
	Choice('BD', name='Bangladesh'),
	Choice('BB', name='Barbados'),
	Choice('BY', name='Belarus'),
	Choice('BE', name='Belgium'),
	Choice('BZ', name='Belize'),
	Choice('BJ', name='Benin'),
	Choice('BM', name='Bermuda'),
	Choice('BT', name='Bhutan'),
	Choice('BO', name='Bolivia (Plurinational State of)'),
	Choice('BQ', name='Bonaire\', Sint Eustatius and Saba'),
	Choice('BA', name='Bosnia and Herzegovina'),
	Choice('BW', name='Botswana'),
	Choice('BV', name='Bouvet Island'),
	Choice('IO', name='British Indian Ocean Territory (the)'),
	Choice('BN', name='Brunei Darussalam'),
	Choice('BG', name='Bulgaria'),
	Choice('BF', name='Burkina Faso'),
	Choice('BI', name='Burundi'),
	Choice('CV', name='Cabo Verde'),
	Choice('KH', name='Cambodia'),
	Choice('CM', name='Cameroon'),
	Choice('CA', name='Canada'),
	Choice('KY', name='Cayman Islands (the)'),
	Choice('CF', name='Central African Republic (the)'),
	Choice('TD', name='Chad'),
	Choice('CL', name='Chile'),
	Choice('CN', name='China'),
	Choice('CX', name='Christmas Island'),
	Choice('CC', name='Cocos (Keeling) Islands (the)'),
	Choice('CO', name='Colombia'),
	Choice('KM', name='Comoros (the)'),
	Choice('CD', name='Congo (the Democratic Republic of the)'),
	Choice('CG', name='Congo (the)'),
	Choice('CK', name='Cook Islands (the)'),
	Choice('CR', name='Costa Rica'),
	Choice('HR', name='Croatia'),
	Choice('CU', name='Cuba'),
	Choice('CW', name='Curaçao'),
	Choice('CY', name='Cyprus'),
	Choice('CZ', name='Czechia'),
	Choice('CI', name='Côte d\'Ivoire'),
	Choice('DK', name='Denmark'),
	Choice('DJ', name='Djibouti'),
	Choice('DM', name='Dominica'),
	Choice('DO', name='Dominican Republic (the)'),
	Choice('EC', name='Ecuador'),
	Choice('EG', name='Egypt'),
	Choice('SV', name='El Salvador'),
	Choice('GQ', name='Equatorial Guinea'),
	Choice('ER', name='Eritrea'),
	Choice('EE', name='Estonia'),
	Choice('SZ', name='Eswatini'),
	Choice('ET', name='Ethiopia'),
	Choice('FK', name='Falkland Islands (the) [Malvinas]'),
	Choice('FO', name='Faroe Islands (the)'),
	Choice('FJ', name='Fiji'),
	Choice('FI', name='Finland'),
	Choice('GF', name='French Guiana'),
	Choice('PF', name='French Polynesia'),
	Choice('TF', name='French Southern Territories (the)'),
	Choice('GA', name='Gabon'),
	Choice('GM', name='Gambia (the)'),
	Choice('GE', name='Georgia'),
	Choice('GH', name='Ghana'),
	Choice('GI', name='Gibraltar'),
	Choice('GR', name='Greece'),
	Choice('GL', name='Greenland'),
	Choice('GD', name='Grenada'),
	Choice('GP', name='Guadeloupe'),
	Choice('GU', name='Guam'),
	Choice('GT', name='Guatemala'),
	Choice('GG', name='Guernsey'),
	Choice('GN', name='Guinea'),
	Choice('GW', name='Guinea-Bissau'),
	Choice('GY', name='Guyana'),
	Choice('HT', name='Haiti'),
	Choice('HM', name='Heard Island and McDonald Islands'),
	Choice('VA', name='Holy See (the)'),
	Choice('HN', name='Honduras'),
	Choice('HK', name='Hong Kong'),
	Choice('HU', name='Hungary'),
	Choice('IS', name='Iceland'),
	Choice('IN', name='India'),
	Choice('ID', name='Indonesia'),
	Choice('IR', name='Iran (Islamic Republic of)'),
	Choice('IQ', name='Iraq'),
	Choice('IE', name='Ireland'),
	Choice('IM', name='Isle of Man'),
	Choice('IL', name='Israel'),
	Choice('JM', name='Jamaica'),
	Choice('JP', name='Japan'),
	Choice('JE', name='Jersey'),
	Choice('JO', name='Jordan'),
	Choice('KZ', name='Kazakhstan'),
	Choice('KE', name='Kenya'),
	Choice('KI', name='Kiribati'),
	Choice('KP', name='Korea (the Democratic People\'s Republic of)'),
	Choice('KR', name='Korea (the Republic of)'),
	Choice('KW', name='Kuwait'),
	Choice('KG', name='Kyrgyzstan'),
	Choice('LA', name='Lao People\'s Democratic Republic (the)'),
	Choice('LV', name='Latvia'),
	Choice('LB', name='Lebanon'),
	Choice('LS', name='Lesotho'),
	Choice('LR', name='Liberia'),
	Choice('LY', name='Libya'),
	Choice('LI', name='Liechtenstein'),
	Choice('LT', name='Lithuania'),
	Choice('LU', name='Luxembourg'),
	Choice('MO', name='Macao'),
	Choice('MG', name='Madagascar'),
	Choice('MW', name='Malawi'),
	Choice('MY', name='Malaysia'),
	Choice('MV', name='Maldives'),
	Choice('ML', name='Mali'),
	Choice('MT', name='Malta'),
	Choice('MH', name='Marshall Islands (the)'),
	Choice('MQ', name='Martinique'),
	Choice('MR', name='Mauritania'),
	Choice('MU', name='Mauritius'),
	Choice('YT', name='Mayotte'),
	Choice('MX', name='Mexico'),
	Choice('FM', name='Micronesia (Federated States of)'),
	Choice('MD', name='Moldova (the Republic of)'),
	Choice('MC', name='Monaco'),
	Choice('MN', name='Mongolia'),
	Choice('ME', name='Montenegro'),
	Choice('MS', name='Montserrat'),
	Choice('MA', name='Morocco'),
	Choice('MZ', name='Mozambique'),
	Choice('MM', name='Myanmar'),
	Choice('NA', name='Namibia'),
	Choice('NR', name='Nauru'),
	Choice('NP', name='Nepal'),
	Choice('NL', name='Netherlands (the)'),
	Choice('NC', name='New Caledonia'),
	Choice('NZ', name='New Zealand'),
	Choice('NI', name='Nicaragua'),
	Choice('NE', name='Niger (the)'),
	Choice('NG', name='Nigeria'),
	Choice('NU', name='Niue'),
	Choice('NF', name='Norfolk Island'),
	Choice('MP', name='Northern Mariana Islands (the)'),
	Choice('NO', name='Norway'),
	Choice('OM', name='Oman'),
	Choice('PK', name='Pakistan'),
	Choice('PW', name='Palau'),
	Choice('PS', name='Palestine\', State of'),
	Choice('PA', name='Panama'),
	Choice('PG', name='Papua New Guinea'),
	Choice('PY', name='Paraguay'),
	Choice('PE', name='Peru'),
	Choice('PH', name='Philippines (the)'),
	Choice('PN', name='Pitcairn'),
	Choice('PR', name='Puerto Rico'),
	Choice('QA', name='Qatar'),
	Choice('MK', name='Republic of North Macedonia'),
	Choice('RO', name='Romania'),
	Choice('RU', name='Russian Federation (the)'),
	Choice('RW', name='Rwanda'),
	Choice('RE', name='Réunion'),
	Choice('BL', name='Saint Barthélemy'),
	Choice('SH', name='Saint Helena\', Ascension and Tristan da Cunha'),
	Choice('KN', name='Saint Kitts and Nevis'),
	Choice('LC', name='Saint Lucia'),
	Choice('MF', name='Saint Martin (French part)'),
	Choice('PM', name='Saint Pierre and Miquelon'),
	Choice('VC', name='Saint Vincent and the Grenadines'),
	Choice('WS', name='Samoa'),
	Choice('SM', name='San Marino'),
	Choice('ST', name='Sao Tome and Principe'),
	Choice('SA', name='Saudi Arabia'),
	Choice('SN', name='Senegal'),
	Choice('RS', name='Serbia'),
	Choice('SC', name='Seychelles'),
	Choice('SL', name='Sierra Leone'),
	Choice('SG', name='Singapore'),
	Choice('SX', name='Sint Maarten (Dutch part)'),
	Choice('SK', name='Slovakia'),
	Choice('SI', name='Slovenia'),
	Choice('SB', name='Solomon Islands'),
	Choice('SO', name='Somalia'),
	Choice('ZA', name='South Africa'),
	Choice('GS', name='South Georgia and the South Sandwich Islands'),
	Choice('SS', name='South Sudan'),
	Choice('ES', name='Spain'),
	Choice('LK', name='Sri Lanka'),
	Choice('SD', name='Sudan (the)'),
	Choice('SR', name='Suriname'),
	Choice('SJ', name='Svalbard and Jan Mayen'),
	Choice('SE', name='Sweden'),
	Choice('SY', name='Syrian Arab Republic'),
	Choice('TW', name='Taiwan (Province of China)'),
	Choice('TJ', name='Tajikistan'),
	Choice('TZ', name='Tanzania\', United Republic of'),
	Choice('TH', name='Thailand'),
	Choice('TL', name='Timor-Leste'),
	Choice('TG', name='Togo'),
	Choice('TK', name='Tokelau'),
	Choice('TO', name='Tonga'),
	Choice('TT', name='Trinidad and Tobago'),
	Choice('TN', name='Tunisia'),
	Choice('TR', name='Turkey'),
	Choice('TM', name='Turkmenistan'),
	Choice('TC', name='Turks and Caicos Islands (the)'),
	Choice('TV', name='Tuvalu'),
	Choice('UG', name='Uganda'),
	Choice('UA', name='Ukraine'),
	Choice('AE', name='United Arab Emirates (the)'),
	Choice('UM', name='United States Minor Outlying Islands (the)'),
	Choice('UY', name='Uruguay'),
	Choice('UZ', name='Uzbekistan'),
	Choice('VU', name='Vanuatu'),
	Choice('VE', name='Venezuela (Bolivarian Republic of)'),
	Choice('VN', name='Viet Nam'),
	Choice('VG', name='Virgin Islands (British)'),
	Choice('VI', name='Virgin Islands (U.S.)'),
	Choice('WF', name='Wallis and Futuna'),
	Choice('EH', name='Western Sahara'),
	Choice('YE', name='Yemen'),
	Choice('ZM', name='Zambia'),
	Choice('ZW', name='Zimbabwe'),
	Choice('AX', name='Åland Islands')
]

LANGUAGE_CODES = [
	Choice('en', name='English'),
	Choice('de', name='German'),
	Choice('fr', name='French'),
	Choice('it', name='Italian'),
	Choice('pt', name='Portuguese'),
	Choice('pl', name='Polish'),
	Separator('------ !! Following language might not be supported !! ------'),
	Choice('aa', name='Afar'),
	Choice('ab', name='Abkhazian'),
	Choice('ae', name='Avestan'),
	Choice('af', name='Afrikaans'),
	Choice('ak', name='Akan'),
	Choice('am', name='Amharic'),
	Choice('an', name='Aragonese'),
	Choice('ar', name='Arabic'),
	Choice('as', name='Assamese'),
	Choice('av', name='Avaric'),
	Choice('ay', name='Aymara'),
	Choice('az', name='Azerbaijani'),
	Choice('ba', name='Bashkir'),
	Choice('be', name='Belarusian'),
	Choice('bg', name='Bulgarian'),
	Choice('bh', name='Bihari'),
	Choice('bi', name='Bislama'),
	Choice('bm', name='Bambara'),
	Choice('bn', name='Bengali'),
	Choice('bo', name='Tibetan'),
	Choice('br', name='Breton'),
	Choice('bs', name='Bosnian'),
	Choice('ca', name='Catalan'),
	Choice('ce', name='Chechen'),
	Choice('ch', name='Chamorro'),
	Choice('co', name='Corsican'),
	Choice('cr', name='Cree'),
	Choice('cs', name='Czech'),
	Choice('cu', name='Old Church Slavonic'),
	Choice('cv', name='Chuvash'),
	Choice('cy', name='Welsh'),
	Choice('da', name='Danish'),
	Choice('dv', name='Divehi'),
	Choice('dz', name='Dzongkha'),
	Choice('ee', name='Ewe'),
	Choice('el', name='Greek'),
	Choice('eo', name='Esperanto'),
	Choice('es', name='Spanish'),
	Choice('et', name='Estonian'),
	Choice('eu', name='Basque'),
	Choice('fa', name='Persian'),
	Choice('ff', name='Fulah'),
	Choice('fi', name='Finnish'),
	Choice('fj', name='Fijian'),
	Choice('fo', name='Faroese'),
	Choice('fy', name='Western Frisian'),
	Choice('ga', name='Irish'),
	Choice('gd', name='Scottish Gaelic'),
	Choice('gl', name='Galician'),
	Choice('gn', name='Guarani'),
	Choice('gu', name='Gujarati'),
	Choice('gv', name='Manx'),
	Choice('ha', name='Hausa'),
	Choice('he', name='Hebrew'),
	Choice('hi', name='Hindi'),
	Choice('ho', name='Hiri Motu'),
	Choice('hr', name='Croatian'),
	Choice('ht', name='Haitian'),
	Choice('hu', name='Hungarian'),
	Choice('hy', name='Armenian'),
	Choice('hz', name='Herero'),
	Choice('ia', name='Interlingua'),
	Choice('id', name='Indonesian'),
	Choice('ie', name='Interlingue'),
	Choice('ig', name='Igbo'),
	Choice('ii', name='Sichuan Yi'),
	Choice('ik', name='Inupiaq'),
	Choice('io', name='Ido'),
	Choice('is', name='Icelandic'),
	Choice('iu', name='Inuktitut'),
	Choice('ja', name='Japanese'),
	Choice('jv', name='Javanese'),
	Choice('ka', name='Georgian'),
	Choice('kg', name='Kongo'),
	Choice('ki', name='Kikuyu'),
	Choice('kj', name='Kwanyama'),
	Choice('kk', name='Kazakh'),
	Choice('kl', name='Greenlandic'),
	Choice('km', name='Khmer'),
	Choice('kn', name='Kannada'),
	Choice('ko', name='Korean'),
	Choice('kr', name='Kanuri'),
	Choice('ks', name='Kashmiri'),
	Choice('ku', name='Kurdish'),
	Choice('kv', name='Komi'),
	Choice('kw', name='Cornish'),
	Choice('ky', name='Kirghiz'),
	Choice('la', name='Latin'),
	Choice('lb', name='Luxembourgish'),
	Choice('lg', name='Ganda'),
	Choice('li', name='Limburgish'),
	Choice('ln', name='Lingala'),
	Choice('lo', name='Lao'),
	Choice('lt', name='Lithuanian'),
	Choice('lu', name='Luba'),
	Choice('lv', name='Latvian'),
	Choice('mg', name='Malagasy'),
	Choice('mh', name='Marshallese'),
	Choice('mi', name='Māori'),
	Choice('mk', name='Macedonian'),
	Choice('ml', name='Malayalam'),
	Choice('mn', name='Mongolian'),
	Choice('mo', name='Moldavian'),
	Choice('mr', name='Marathi'),
	Choice('ms', name='Malay'),
	Choice('mt', name='Maltese'),
	Choice('my', name='Burmese'),
	Choice('na', name='Nauru'),
	Choice('nb', name='Norwegian Bokmål'),
	Choice('nd', name='North Ndebele'),
	Choice('ne', name='Nepali'),
	Choice('ng', name='Ndonga'),
	Choice('nl', name='Dutch'),
	Choice('nn', name='Norwegian Nynorsk'),
	Choice('no', name='Norwegian'),
	Choice('nr', name='South Ndebele'),
	Choice('nv', name='Navajo'),
	Choice('ny', name='Chichewa'),
	Choice('oc', name='Occitan'),
	Choice('oj', name='Ojibwa'),
	Choice('om', name='Oromo'),
	Choice('or', name='Oriya'),
	Choice('os', name='Ossetian'),
	Choice('pa', name='Panjabi'),
	Choice('pi', name='Pāli'),
	Choice('ps', name='Pashto'),
	Choice('qu', name='Quechua'),
	Choice('rc', name='Reunionese'),
	Choice('rm', name='Romansh'),
	Choice('rn', name='Kirundi'),
	Choice('ro', name='Romanian'),
	Choice('ru', name='Russian'),
	Choice('rw', name='Kinyarwanda'),
	Choice('sa', name='Sanskrit'),
	Choice('sc', name='Sardinian'),
	Choice('sd', name='Sindhi'),
	Choice('se', name='Northern Sami'),
	Choice('sg', name='Sango'),
	Choice('sh', name='Serbo-Croatian'),
	Choice('si', name='Sinhalese'),
	Choice('sk', name='Slovak'),
	Choice('sl', name='Slovenian'),
	Choice('sm', name='Samoan'),
	Choice('sn', name='Shona'),
	Choice('so', name='Somali'),
	Choice('sq', name='Albanian'),
	Choice('sr', name='Serbian'),
	Choice('ss', name='Swati'),
	Choice('st', name='Sotho'),
	Choice('su', name='Sundanese'),
	Choice('sv', name='Swedish'),
	Choice('sw', name='Swahili'),
	Choice('ta', name='Tamil'),
	Choice('te', name='Telugu'),
	Choice('tg', name='Tajik'),
	Choice('th', name='Thai'),
	Choice('ti', name='Tigrinya'),
	Choice('tk', name='Turkmen'),
	Choice('tl', name='Tagalog'),
	Choice('tn', name='Tswana'),
	Choice('to', name='Tonga'),
	Choice('tr', name='Turkish'),
	Choice('ts', name='Tsonga'),
	Choice('tt', name='Tatar'),
	Choice('tw', name='Twi'),
	Choice('ty', name='Tahitian'),
	Choice('ug', name='Uighur'),
	Choice('uk', name='Ukrainian'),
	Choice('ur', name='Urdu'),
	Choice('uz', name='Uzbek'),
	Choice('ve', name='Venda'),
	Choice('vi', name='Viêt Namese'),
	Choice('vo', name='Volapük'),
	Choice('wa', name='Walloon'),
	Choice('wo', name='Wolof'),
	Choice('xh', name='Xhosa'),
	Choice('yi', name='Yiddish'),
	Choice('yo', name='Yoruba'),
	Choice('za', name='Zhuang'),
	Choice('zh', name='Chinese'),
	Choice('zu', name='Zulu')
]


def isAdmin() -> bool:
	try:
		return os.getuid() == 0
	except AttributeError:
		return ctypes.windll.shell32.IsUserAnAdmin() != 0


@click.command(name='discover')
@click.option('-n', '--network', required=False, type=str, default='')
@click.option('-a', '--all_devices', is_flag=True)
@click.pass_context
def discover(ctx: click.Context, network: str, all_devices: bool, return_to_main_menu: bool = True):  # NOSONAR
	click.clear()
	click.secho('Discovering devices on your network, please wait', fg='yellow')

	ip = IP_REGEX.search(socket.gethostbyname(socket.gethostname()))
	if not ip and not network:
		printError("Couldn't retrieve local ip address")
	else:
		if not network:
			network = f"{'.'.join(ip[0].split('.')[0:3])}.0/24"

		click.secho(f'Scanning network: {network}', fg='yellow')
		waitAnimation()
		scan = networkscan.Networkscan(network)
		scan.run()

		if all_devices:
			click.secho('Discovered devices:', fg='yellow')
		else:
			click.secho('Discovered potential devices:', fg='yellow')

		devices = list()
		for device in scan.list_of_hosts_found:
			try:
				name = socket.gethostbyaddr(device)
				if not name:
					continue

				if all_devices or (not all_devices and ('projectalice' in name[0].lower() or 'raspberrypi' in name[0].lower())):
					click.secho(f'{device}: {name[0].replace(".home", "")}', fg='yellow')
					devices.append(device)
			except:
				continue  # If no name, we don't need the device anyway

		stopAnimation()

		devices.append('Return to main menu')  # NOSONAR
		device = inquirer.select(
			message='Select the device you want to connect to',
			choices=devices
		).execute()

		if device == 'Return to main menu':
			returnToMainMenu(ctx)
		else:
			ctx.invoke(connect, ip_address=device, return_to_main_menu=return_to_main_menu)

	if return_to_main_menu:
		returnToMainMenu(ctx)


@click.command(name='connect')
@click.option('-i', '--ip_address', required=False, type=str, default='')
@click.option('-p', '--port', required=False, type=int, default=22)
@click.option('-u', '--user', required=False, type=str)
@click.option('-pw', '--password', required=False, type=str, default='')
@click.option('-r', '--return_to_main_menu', required=False, type=bool, default=True)
@click.pass_context
def connect(ctx: click.Context, ip_address: str, port: int, user: str, password: str, return_to_main_menu: bool, noExceptHandling: bool = False) -> Optional[paramiko.SSHClient]:  # NOSONAR
	global SSH, IP_REGEX, CONNECTED_TO
	remoteAuthorizedKeysFile = '~/.ssh/authorized_keys'
	confFile = Path(Path.home(), '.pacli/configs.json')
	confFile.parent.mkdir(parents=True, exist_ok=True)
	if not confFile.exists():
		confs = dict()
		confs['servers'] = dict()
		confFile.write_text(json.dumps(confs))
	else:
		confs = json.loads(confFile.read_text())

	if not ip_address:
		ip_address = inquirer.text(
			message='Please enter the device IP address',
			validate=lambda ip: IP_REGEX.match(ip) is not None
		).execute()

	data = confs['servers'].get(ip_address, dict()).get('keyFile')
	if data:
		user = confs['servers'][ip_address]['user']
		keyFile = Path(Path.home(), f".ssh/{confs['servers'][ip_address]['keyFile']}")

		if not keyFile.exists():
			printError('Declared server is using a non existing RSA key file, removing entry and asking for password.')
			confs['servers'].pop(ip_address, None)
			keyFile = None
	else:
		keyFile = None

	if not keyFile and not user:
		user = inquirer.text(
			message='Please enter username',
			validate=lambda answer: len(answer) > 0,
			invalid_message='Cannot be empty'
		).execute()

	if not keyFile and not password:
		password = inquirer.secret(
			message='Please enter the connection password',
			transformer=lambda _: HIDDEN
		).execute()

	try:
		if SSH:
			disconnect()

		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)

		waitAnimation()

		if password:
			ssh.connect(hostname=ip_address, port=port, username=user, password=password)
		else:
			key = paramiko.RSAKey.from_private_key_file(str(keyFile))
			ssh.connect(hostname=ip_address, port=port, username=user, pkey=key)

	except Exception as e:
		if not noExceptHandling:
			printError(f'Failed connecting to device: {e}')
			if ip_address in confs['servers'] and not password:
				confs['servers'].pop(ip_address, None)
				confFile.write_text(json.dumps(confs))
				ctx.invoke(connect, ip_address=ip_address, user=user, return_to_main_menu=return_to_main_menu)
				return
		else:
			raise
	else:
		printSuccess('Successfully connected to device')
		SSH = ssh
		CONNECTED_TO = ip_address
		if ip_address not in confs['servers']:
			filename = f'id_rsa_{str(uuid.uuid4())}'
			keyFile = Path(Path.home(), f'.ssh/{filename}')
			confs['servers'][ip_address] = {
				'keyFile': filename,
				'user'   : user
			}
			confFile.write_text(json.dumps(confs))

			key = paramiko.RSAKey.generate(4096)
			key.write_private_key_file(filename=str(keyFile))

			pubKeyFile = keyFile.with_suffix('.pub')
			pubKeyFile.write_text(key.get_base64())
			sshCmd(f"echo \"ssh-rsa {pubKeyFile.read_text()} Project Alice RSA key\" | exec sh -c 'cd ; umask 077 ; mkdir -p .ssh && cat >> {remoteAuthorizedKeysFile} || exit 1 ; if type restorecon >/dev/null 2>&1 ; then restorecon -F .ssh ${remoteAuthorizedKeysFile} ; fi'")

		if not return_to_main_menu:
			return ssh

	if return_to_main_menu:
		returnToMainMenu(ctx)


def printError(text: str):
	ANIMATION_FLAG.clear()
	click.secho(message=f'✘ {text}', fg='red')
	time.sleep(2)


def printSuccess(text: str):
	ANIMATION_FLAG.clear()
	click.secho(message=f'✔ {text}', fg='green')
	time.sleep(2)


def printInfo(text: str):
	ANIMATION_FLAG.clear()
	click.secho(message=f'▷ {text}', fg='yellow')
	time.sleep(0.5)


def disconnect():
	global SSH, CONNECTED_TO
	if SSH:
		SSH.close()
		SSH = None
		CONNECTED_TO = ''
		printSuccess('Disconnected')


def waitAnimation():
	global ANIMATION_THREAD

	if ANIMATION_FLAG.is_set():
		ANIMATION_FLAG.clear()

	if ANIMATION_THREAD:
		ANIMATION_THREAD.join(timeout=1)

	ANIMATION_THREAD = Thread(target=_animation, daemon=True)
	ANIMATION_THREAD.start()
	time.sleep(1)


def ctrlCExplained():
	global ANIMATION_THREAD

	if ANIMATION_FLAG.is_set():
		ANIMATION_FLAG.clear()

	if ANIMATION_THREAD:
		ANIMATION_THREAD.join(timeout=1)

	ANIMATION_THREAD = Thread(target=_ctrlCExplained, daemon=True)
	ANIMATION_THREAD.start()
	time.sleep(1)


def stopAnimation():
	ANIMATION_FLAG.clear()


def _animation():
	animation = '|/-\\'
	idx = 0
	ANIMATION_FLAG.set()
	while ANIMATION_FLAG.is_set():
		click.secho(animation[idx % len(animation)] + '\r', nl=False, fg='yellow')
		idx += 1
		time.sleep(0.1)


def _ctrlCExplained():
	ANIMATION_FLAG.set()
	while ANIMATION_FLAG.is_set():
		try:
			click.secho(f'\rPress CTRL-C to quit\r', nl=False, fg='yellow')
			time.sleep(0.1)
		except KeyboardInterrupt:
			ANIMATION_FLAG.clear()
			raise KeyboardInterrupt


def askReturnToMainMenu(ctx: click.Context):
	confirm = inquirer.confirm(message='Do you want to return to main menu?', default=True).execute()
	if confirm:
		returnToMainMenu(ctx)
	else:
		sys.exit(0)


def returnToMainMenu(ctx: click.Context, pause: bool = False, message: str = ''):
	import AliceCli.MainMenu as MainMenu

	stopAnimation()
	if pause:
		click.echo(message)
		click.pause('Press any key to continue')

	ctx.invoke(MainMenu.mainMenu)


def validateHostname(hostname: str) -> str:
	if not hostname:
		raise click.BadParameter('Hostname cannot be empty')

	if len(hostname) > 253:
		raise click.BadParameter('Hostname maximum length is 253')

	allowed = re.compile(r'^\w([\w-]*\w)?$', re.IGNORECASE)
	if allowed.match(hostname):
		return hostname
	else:
		raise click.BadParameter('Hostname cannot contain special characters')


def sshCmd(cmd: str, hide: bool = False):
	stdin, stdout, stderr = SSH.exec_command(cmd)

	while line := stdout.readline():
		if not hide:
			click.secho(line, nl=False, fg='cyan', italic=True)  # NOSONAR


def sshCmdWithReturn(cmd: str) -> Tuple:
	stdin, stdout, stderr = SSH.exec_command(cmd)
	return stdout, stderr


# noinspection DuplicatedCode
def getUpdateSource(name: str, definedSource: str) -> str:
	updateSource = 'master'
	if definedSource in {'master', 'release'}:
		return updateSource

	# noinspection PyUnboundLocalVariable
	req = requests.get(f'https://api.github.com/repos/project-alice-assistant/{name}/branches')
	result = req.json()

	versions = list()
	for branch in result:
		repoVersion = Version.fromString(branch['name'])

		releaseType = repoVersion.releaseType
		if not repoVersion.isVersionNumber \
				or definedSource == 'rc' and releaseType in {'b', 'a'} \
				or definedSource == 'beta' and releaseType == 'a':
			continue

		versions.append(repoVersion)

	if versions:
		versions.sort(reverse=True)
		updateSource = versions[0]

	return str(updateSource)


def tryReconnect(ctx: click.Context, address: str) -> bool:
	rebooted = False
	for i in range(1, 5):
		try:
			printInfo(f'Trying to contact device, attempt {i} of 5...')
			ctx.invoke(connect, ip_address=address, return_to_main_menu=False, noExceptHandling=True)
			if SSH:
				rebooted = True
				break
			time.sleep(5)
		except:
			pass  # Let's try again...

	return rebooted
