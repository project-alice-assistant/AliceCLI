import AliceCli.utils.commons as commons

def checkConnection(func):
	def wrapper(*args, **kwargs):
		if not commons.SSH:
			commons.printError('Please connect to a server first')
			args[0].invoke(commons.discover, return_to_main_menu=False)

		func(args[0], **kwargs)
	return wrapper
