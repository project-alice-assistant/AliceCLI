import AliceCli.utils.commons as commons
from AliceCli.utils import utils


def checkConnection(func):
	def wrapper(*args):
		if not commons.SSH:
			commons.printError('Please connect to a server first')
			args[0].invoke(utils.connect, return_to_main_menu=False)

		func(args[0])
	return wrapper
