import time
import pathlib


logToFile = True
logToScreen = True


def log_To_Screen(logging, **kwargs):
    print(logging)


def log_To_File(logging):
    logging_path = "/home/pi/python/smart-photo-frame/" + "message.log"
    logfile = open(logging_path, "a")
    datetime = time.strftime("%b %d %Y %H:%M:%S")
    log = str(datetime) + " " + str(logging) + "\n"
    logfile.write(log)
    logfile.close()


def log(logging):
    if logToFile == True:
        log_To_File(logging)
    if logToScreen == True:
        log_To_Screen(logging)