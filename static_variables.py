import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# FRAME VARIABLES
timer = 10
blend = 750    # in milliseconds


# IMAP STATICS
EMAIL_ACCOUNT = config['gmail']['account']
EMAIL_PASS = config['gmail']['password']


# TELEGRAM STATICS
token = config['telegram']['token']
