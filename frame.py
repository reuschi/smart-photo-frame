import os
import subprocess
import time
import imap
import telegram
import module_log
import glob
import pathlib
import static_variables
import RPi.GPIO as GPIO


images = []
timer = static_variables.timer
blend = static_variables.blend    # in milliseconds

# Initialize GPIOs für Buttons
GPIO.setmode(GPIO.BCM)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def exit_Slideshow():
    try:
        os.system("sudo killall -15 fbi")
        module_log.log("Slideshow killed")
    except Exception as e:
        module_log.log(e)


def delete_Old_Files(directory="images", max=50):
    module_log.log("Checking for old files to be deleted...")
    file_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / directory / "*.*")
    delete = False

    files = glob.glob(str(file_path))
    files.sort(key=os.path.getmtime, reverse=True)

    for x in range(max, len(files)):
        try:
            os.remove(files[x])
            delete = True
        except Exception as e:
            module_log.log("Removing the file {} was NOT successful: {}".format(files[x], e))

    if delete:
        module_log.log("Deleting old files is done.")
    else:
        module_log.log("There were no files to be deleted.")


def run_Slideshow(path='images'):
    path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / path / "*.*")
    bashCommand = "sudo fbi --noverbose --random --blend {} -a -t {} -T 1 {}".format(blend, timer, path)
    process = subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.5)

    module_log.log("Slideshow running")


def restart_Slideshow():
    module_log.flush_Log_File()
    module_log.log("Slideshow restarting")
    exit_Slideshow()
    delete_Old_Files()
    run_Slideshow()


def rise_Timer(channel):
    # rise timer of presentation, to lower the frequency
    global timer

    timer += 2
    restart_Slideshow()


def lower_Timer(channel):
    # lower timer of presentation, to rise the frequency
    global timer

    if timer >= 4:
        timer -= 2
        restart_Slideshow()
    else:
        module_log.log(f"Timer already at: {timer}. Lowering not possible!")


def system_Shut_Down(channel):
    # Shutdown system
    module_log.log("!!!! SYSTEM IS GOING TO SHUTDOWN !!!!")
    os.system("sudo poweroff")
    time.sleep(1)


if __name__ == '__main__':

    restart_Slideshow()

    i = 0

    # Rise presentation Timer
    GPIO.add_event_detect(13, GPIO.FALLING, callback=rise_Timer, bouncetime=400)

    # Lower presentation timer
    GPIO.add_event_detect(23, GPIO.FALLING, callback=lower_Timer, bouncetime=400)

    # Shutdown the system
    GPIO.add_event_detect(26, GPIO.FALLING, callback=system_Shut_Down, bouncetime=400)

    while True:
        if i >= 7:
            mail = imap.main()
            i = 0
        else:
            i += 1
            mail = False

        tg = telegram.main()

        if tg or mail:
            restart_Slideshow()

        time.sleep(15)



