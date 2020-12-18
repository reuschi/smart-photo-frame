import configparser
import pathlib


config = configparser.ConfigParser()
config.read(pathlib.Path(pathlib.Path(__file__).parent.absolute() / 'config.ini'))


# FRAME VARIABLES
# ------------------------------
timer = 10
blend = 750    # in milliseconds


# IMAP STATICS
# ------------------------------
EMAIL_ACCOUNT = config['gmail']['account']
EMAIL_PASS = config['gmail']['password']


# TELEGRAM STATICS
# ------------------------------
token = config['telegram']['token']

# Fetch allowed senders
elements = config.get('telegram', 'allowedsenders').split(',')
tg_allowed_senders = [int(x) for x in elements]


# LOGGING VARIABLES
# ------------------------------
logToFile = bool(config['logging']['logToFile'])
logToScreen = bool(config['logging']['logToScreen'])
#logToFile = True
#logToScreen = True