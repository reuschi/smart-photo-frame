""" Generating static variables for all modules """

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
verbose = config.getboolean('frame', 'verbose')


# IMAP STATICS
# ------------------------------
EMAIL_ACCOUNT = config['mail']['account']
EMAIL_PASS = config['mail']['password']
EMAIL_HOST = config['mail']['hostname']
mail_elements = config.get('mail', 'fileExtensions').split(',')
file_extensions = [str(ext) for ext in mail_elements]


# TELEGRAM STATICS
# ------------------------------
token = config['telegram']['token']
status_signal = config.getboolean('telegram', 'status_signal')
poll_timeout = int(config['telegram']['poll_timeout'])

# Fetch allowed senders
tg_elements = config.get('telegram', 'allowedsenders').split(',')
tg_allowed_senders = [int(x) for x in tg_elements]
# Fetch allowed admins
tg_admin_elements = config.get('telegram', 'admins').split(',')
tg_allowed_admins = [int(x) for x in tg_admin_elements]
# Fetch Bot commands
tg_bot_commands = literal_eval(config['telegram']['commands'])
#tg_bot_commands = [int(x) for x in tg_commands_elements]


# OWNCLOUD STATICS
# ------------------------------
oc_host = config['owncloud']['host']
oc_username = config['owncloud']['username']
oc_password = config['owncloud']['password']
oc_delete = config.getboolean('owncloud', 'delete_after_download')
oc_subfolder = config['owncloud']['subfolder']


# LOGGING VARIABLES
# ------------------------------
logToFile = config.getboolean('logging', 'logToFile')
logToScreen = config.getboolean('logging', 'logToScreen')


def add_value_to_config(section: str, parameter: str, value: str):
    """ Add a new 'value' to a 'parameter' in 'section' in the config file """

    config[section][parameter] += "," + str(value)
    with open(config_path, 'w', encoding="utf-8") as conf:
        config.write(conf)


def change_config_value(section: str, parameter: str, value: str):
    """ Change 'value' of a 'parameter' in 'section' in the config file """

    config[section][parameter] = str(value)
    with open(config_path, 'w', encoding="utf-8") as conf:
        config.write(conf)
