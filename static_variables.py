import configparser
import pathlib
from ast import literal_eval


config = configparser.ConfigParser()
config_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / 'config.ini')
config.read(config_path)

# GLOBAL
# ------------------------------
language = config['global']['language']


# FRAME VARIABLES
# ------------------------------
timer = int(config['frame']['timer'])
blend = int(config['frame']['blend'])    # in milliseconds
photocount = int(config['frame']['photocount'])


# IMAP STATICS
# ------------------------------
EMAIL_ACCOUNT = config['gmx']['account']
EMAIL_PASS = config['gmx']['password']
EMAIL_HOST = config['gmx']['hostname']
mail_elements = config.get('gmx', 'fileExtensions').split(',')
file_extensions = [str(ext) for ext in mail_elements]


# TELEGRAM STATICS
# ------------------------------
token = config['telegram']['token']
status_signal = config.getboolean('telegram', 'status_signal')

# Fetch allowed senders
tg_elements = config.get('telegram', 'allowedsenders').split(',')
tg_allowed_senders = [int(x) for x in tg_elements]
# Fetch allowed admins
tg_admin_elements = config.get('telegram', 'admins').split(',')
tg_allowed_admins = [int(x) for x in tg_admin_elements]
# Fetch Bot commands
tg_bot_commands = literal_eval(config['telegram']['commands'])
#tg_bot_commands = [int(x) for x in tg_commands_elements]


# LOGGING VARIABLES
# ------------------------------
logToFile = config.getboolean('logging', 'logToFile')
logToScreen = config.getboolean('logging', 'logToScreen')


def add_value_to_config(section: str, parameter: str, value: str):
    # Add a new 'value' to a 'parameter' in 'section' in the config file
    config[section][parameter] += "," + str(value)
    with open(config_path, 'w') as conf:
        config.write(conf)


def change_config_value(section: str, parameter: str, value: str):
    # Change 'value' of a configured 'parameter' in 'section'
    config[section][parameter] = str(value)
    with open(config_path, 'w') as conf:
        config.write(conf)

