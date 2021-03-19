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
#images = []
#timer = static_variables.timer
#blend = static_variables.blend    # in milliseconds
#photocount = static_variables.photocount

# Initialize GPIOs für Buttons
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(9, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)


class Frame:

    def __init__(self):
        self.images = []
        self.timer = static_variables.timer
        self.blend = static_variables.blend  # in milliseconds
        self.photocount = static_variables.photocount

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(9, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def exit_slideshow(self):
        # Kill all running processes of the slideshow
        try:
            os.system("sudo killall -15 fbi")
            module_log.log("Slideshow killed")
        except Exception as e:
            module_log.log(e)

    def delete_old_files(self, directory: str = "images", max: int = None):
        # Delete older image files in 'directory' that are over amount 'max'
        if max is None:
            max = self.photocount

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

    def run_slideshow(self, path: str = "images"):
        # Start the slideshow with all present files in subfolder defined in variable 'path'
        path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / path / "*.*")
        bash_command = f"sudo fbi --noverbose --random --blend {self.blend} -a -t {self.timer} -T 1 {path}"
        process = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.5)

        module_log.log("Slideshow running")

    def restart_slideshow(self):
        # Stop slideshow and restart the slideshow with the new added image files
        module_log.flush_log_file()
        module_log.log("Slideshow restarting")
        self.exit_slideshow()
        self.delete_old_files()
        self.run_slideshow()

    def rise_timer(self, channel):
        # Rise timer of presentation, to lower the showing frequency
        self.timer += 2
        module_log.log(f"Timer raised to: {self.timer}.")
        self.restart_slideshow()

    def lower_timer(self, channel):
        # Lower timer of presentation, to rise the showing frequency
        if self.timer >= 4:
            self.timer -= 2
            module_log.log(f"Timer lowered to: {self.timer}.")
            self.restart_slideshow()
        else:
            module_log.log(f"Timer already at: {self.timer}. Lowering not possible!")

    def system_shutdown(self, channel):
        # Shutdown the whole system
        module_log.log("!!!! SYSTEM IS GOING TO SHUTDOWN !!!!")
        os.system("sudo poweroff")
        time.sleep(1)


if __name__ == "__main__":
    frame = Frame()

    module_log.log("!!!! SYSTEM STARTED !!!!")
    frame.restart_slideshow()

    i = 0

    # Rise presentation Timer
    GPIO.add_event_detect(27, GPIO.FALLING, callback=frame.rise_timer, bouncetime=400)

    # Lower presentation Timer
    GPIO.add_event_detect(19, GPIO.FALLING, callback=frame.lower_timer, bouncetime=400)

    # Shutdown the system
    GPIO.add_event_detect(9, GPIO.FALLING, callback=frame.system_shutdown, bouncetime=400)

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
            frame.restart_slideshow()

        time.sleep(15)



