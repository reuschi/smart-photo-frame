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


# Initialize static variables
images = []
timer = static_variables.timer
blend = static_variables.blend    # in milliseconds
photocount = static_variables.photocount

# Initialize GPIOs für Buttons
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(9, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def exit_Slideshow():
    # Kill all running processes of the slideshow
    try:
        os.system("sudo killall -15 fbi")
        module_log.log("Slideshow killed")
    except Exception as e:
        module_log.log(e)


def delete_Old_Files(directory="images", max=photocount):
    # Delete older image files in 'directory' that are over amount 'max'
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
            module_log.log(f"Removing the file {files[x]} was NOT successful: {e}")

    if delete:
        module_log.log("Deleting old files is done.")
    else:
        module_log.log("There were no files to be deleted.")


def run_Slideshow(path='images'):
    # Start the slideshow with all present files in subfolder defined in variable 'path'
    path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / path / "*.*")
    bashCommand = f"sudo fbi --noverbose --random --blend {blend} -a -t {timer} -T 1 {path}"
    process = subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.5)

    module_log.log("Slideshow running")


def restart_Slideshow():
    # Stop slideshow and restart the slideshow with the new added image files
    module_log.flush_Log_File()
    module_log.log("Slideshow restarting")
    exit_Slideshow()
    delete_Old_Files()
    run_Slideshow()


def rise_Timer(channel):
    # Rise timer of presentation, to lower the showing frequency
    global timer

    timer += 2
    module_log.log(f"Timer raised to: {timer}.")
    restart_Slideshow()


def lower_Timer(channel):
    # Lower timer of presentation, to rise the showing frequency
    global timer

    if timer >= 4:
        timer -= 2
        module_log.log(f"Timer lowered to: {timer}.")
        restart_Slideshow()
    else:
        module_log.log(f"Timer already at: {timer}. Lowering not possible!")


def system_Shut_Down(channel):
    # Shutdown the whole system
    module_log.log("!!!! SYSTEM IS GOING TO SHUTDOWN !!!!")
    os.system("sudo poweroff")
    time.sleep(1)


if __name__ == '__main__':
    module_log.log("!!!! SYSTEM STARTED !!!!")
    restart_Slideshow()

    i = 0

    # Rise presentation Timer
    GPIO.add_event_detect(27, GPIO.FALLING, callback=rise_Timer, bouncetime=400)

    # Lower presentation Timer
    GPIO.add_event_detect(19, GPIO.FALLING, callback=lower_Timer, bouncetime=400)

    # Shutdown the system
    GPIO.add_event_detect(9, GPIO.FALLING, callback=system_Shut_Down, bouncetime=400)

    while True:
        # Request for new mails every 2 minutes
        if i >= 7:
            mail = imap.main()
            i = 0
        else:
            i += 1
            mail = False

        # Request for new Telegram message
        tg = telegram.main()

        # If new images received by mail or Telegram restart the slideshow with the new images
        if tg or mail:
            restart_Slideshow()

        time.sleep(15)



