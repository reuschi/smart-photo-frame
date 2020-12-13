import time


logToFile = True
logToScreen = True


def log_To_Screen(logging, **kwargs):
    print(logging)


def log_To_File(logging):
    logfile = open("message.log", "a")
    datetime = time.strftime("%b %d %Y %H:%M:%S")
    log = datetime + " " + logging + "\n"
    logfile.write(log)
    logfile.close()


def log(logging):
    if logToFile == True:
        log_To_File(logging)
    if logToScreen == True:
        log_To_Screen(logging)