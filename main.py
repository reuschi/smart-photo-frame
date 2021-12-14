import time
from imap import ImapMail
from frame import Frame
from telegram import Telegram
from owncloud import Owncloud
import module_log
import static_variables
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(9, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)


if __name__ == "__main__":
    frame = Frame(static_variables.timer, static_variables.blend, static_variables.photocount)
    imap = ImapMail(static_variables.EMAIL_ACCOUNT, static_variables.EMAIL_PASS, hostname=static_variables.EMAIL_HOST, ext=static_variables.file_extensions)
    tg = Telegram(static_variables.token, static_variables.tg_allowed_senders, static_variables.tg_allowed_admins)
    oc = Owncloud(static_variables.oc_host, static_variables.oc_username, static_variables.oc_password)
    tg.set_commands()
    tg.send_signal()

    module_log.log("!!!! SYSTEM STARTED !!!!")
    frame.restart_slideshow()

    # Rise presentation Timer
    GPIO.add_event_detect(27, GPIO.FALLING, callback=frame.rise_timer, bouncetime=400)

    # Lower presentation Timer
    GPIO.add_event_detect(19, GPIO.FALLING, callback=frame.lower_timer, bouncetime=400)

    # Shutdown the system
    GPIO.add_event_detect(9, GPIO.FALLING, callback=frame.system_shutdown, bouncetime=400)

    # Set current time to 120 seconds in the past
    reference_time = int(time.time()) - 120

    while True:
        try:
            # Request for new mails every 120 seconds
            if int(time.time()) >= reference_time + 120:
                mail = imap.init_imap(static_variables.EMAIL_ACCOUNT, static_variables.EMAIL_PASS)
                reference_time = int(time.time())
            else:
                mail = False

            # Request for new images on Owncloud
            owncloud = oc.download_file()

            # If new images received by mail or Owncloud restart the slideshow with the new images
            if mail or owncloud:
                frame.restart_slideshow()

            # Request for new Telegram message
            telegram = tg.process_new_message()

            # If new images received by Telegram restart the slideshow with the new images
            if telegram:
                frame.restart_slideshow()

        except KeyboardInterrupt:
            # Terminate the script
            module_log.log("Script interrupted by terminal input")

