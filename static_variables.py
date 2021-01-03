import configparser
import pathlib


config = configparser.ConfigParser()
config.read(pathlib.Path(pathlib.Path(__file__).parent.absolute() / 'config.ini'))


# FRAME VARIABLES
# ------------------------------
timer = int(config['frame']['timer'])
blend = int(config['frame']['blend'])    # in milliseconds
photocount = int(config['frame']['photocount'])


# IMAP STATICS
# ------------------------------
EMAIL_ACCOUNT = config['gmail']['account']
EMAIL_PASS = config['gmail']['password']
mail_elements = config.get('gmail', 'fileExtension').split(',')
fileExtensions = [str(ext) for ext in mail_elements]


# TELEGRAM STATICS
# ------------------------------
token = config['telegram']['token']

# Fetch allowed senders
tg_elements = config.get('telegram', 'allowedsenders').split(',')
tg_allowed_senders = [int(x) for x in tg_elements]


# LOGGING VARIABLES
# ------------------------------
logToFile = bool(config['logging']['logToFile'])
logToScreen = bool(config['logging']['logToScreen'])
#logToFile = True
#logToScreen = True
