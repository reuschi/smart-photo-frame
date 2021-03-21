import time
import pathlib
import static_variables


logToFile = static_variables.logToFile
logToScreen = static_variables.logToScreen
logging_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "message.log")


def log_to_screen(logging, **kwargs):
    print(f"{logging}", flush=True)


def log_to_file(logging):
    logfile = open(logging_path, "a")
    datetime = time.strftime("%b %d %Y %H:%M:%S")
    logger = str(datetime) + " " + str(logging) + "\n"
    logfile.write(logger)
    logfile.close()


def log(logging):
    if logToFile:
        log_to_file(logging)
    if logToScreen:
        log_to_screen(logging)


def flush_log_file(max=100000):
    # Delete lines of logging file that are over 'max' amount
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
