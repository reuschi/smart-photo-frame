import configparser
import pathlib


config = configparser.ConfigParser()
config_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / 'config.ini')
config.read(config_path)


# FRAME VARIABLES
# ------------------------------
timer = int(config['frame']['timer'])
blend = int(config['frame']['blend'])    # in milliseconds
photocount = int(config['frame']['photocount'])


# IMAP STATICS
# ------------------------------
EMAIL_ACCOUNT = config['gmail']['account']
EMAIL_PASS = config['gmail']['password']
mail_elements = config.get('gmail', 'fileExtensions').split(',')
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


def add_Value_To_Config(section: str, parameter: str, value: str):
    # Add a new 'value' to a 'parameter' in 'section' in the config file
    config[section][parameter] += "," + str(value)
    with open(config_path, 'w') as conf:
        config.write(conf)

