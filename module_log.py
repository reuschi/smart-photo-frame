""" Logging Module """

import time

import pathlib
import static_variables


logToFile = static_variables.logToFile
logToScreen = static_variables.logToScreen
logging_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "message.log")


def log_to_screen(logging):
    """ Log to screen/clonsole """

    print(f"{logging}", flush=True)


def log_to_file(logging):
    """ Log to a file """

    datetime = time.strftime("%b %d %Y %H:%M:%S")
    logger = str(datetime) + " " + str(logging) + "\n"
    with open(logging_path, "a", encoding="utf-8") as logfile:
        logfile.write(logger)


def log(logging):
    """ Call functions regarding on the configuration values """

    if logToFile:
        log_to_file(logging)
    if logToScreen:
        log_to_screen(logging)


def flush_log_file(maximum=100000):
    """ Delete lines of logging file that are over 'max' amount """

    count = 0

    with open(logging_path, encoding="utf-8") as file:
        for count, _value in enumerate(file):
            pass

    result = count + 1 - maximum

    if result > 0:
        log("Flushing log file")

        with open(logging_path, "r+", encoding="utf-8") as file:
            line = file.readlines()
            file.seek(0)
            j = 1
            for text in line:
                if j > result:
                    file.write(text)
                j += 1
            file.truncate()

        log("Flushing done!")
