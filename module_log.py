import time
import pathlib
import static_variables


logToFile = static_variables.logToFile
logToScreen = static_variables.logToScreen
logging_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "message.log")


def log_To_Screen(logging, **kwargs):
    print(logging)


def log_To_File(logging):
    # logging_path = "/home/pi/python/smart-photo-frame/" + "message.log"
    # logging_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "message.log")
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


def flush_Log_File(max=100000):
    with open(logging_path) as f:
        for i, l in enumerate(f):
            pass

    result = i + 1 - max

    if result > 0:
        log("Flushing log file")

        with open(logging_path, "r+") as file:
            line = file.readlines()
            file.seek(0)
            j = 1
            for text in line:
                if j > result:
                    file.write(text)
                j += 1
            file.truncate()

        log("Flushing done!")
