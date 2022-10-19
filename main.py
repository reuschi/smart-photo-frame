""" Main file to start the Smart Photo Frame """

import time

from RPi import GPIO
from imap import ImapMail
from frame import Frame
from telegram import Telegram
from owncloud import Owncloud
import module_log
import static_variables


GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(9, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)


if __name__ == "__main__":
    frame = Frame(static_variables.timer, static_variables.blend, static_variables.photocount)
    imap = ImapMail(static_variables.EMAIL_ACCOUNT, static_variables.EMAIL_PASS,
                    static_variables.EMAIL_HOST, static_variables.file_extensions)
    tg = Telegram(static_variables.token, static_variables.tg_allowed_senders,
                  static_variables.tg_allowed_admins)
    oc = Owncloud(static_variables.oc_host, static_variables.oc_username,
                  static_variables.oc_password)
    tg.set_commands()
    tg.send_signal()

    module_log.log("!!!! SYSTEM STARTED !!!!")
    frame.restart_slideshow(static_variables.verbose)

    # Rise presentation Timer
    GPIO.add_event_detect(27, GPIO.FALLING, callback=frame.rise_timer, bouncetime=400)

    # Lower presentation Timer
    GPIO.add_event_detect(19, GPIO.FALLING, callback=frame.lower_timer, bouncetime=400)

    # Shutdown the system
    GPIO.add_event_detect(9, GPIO.FALLING, callback=frame.system_shutdown, bouncetime=400)

    # Set current time to 120 seconds in the past
    reference_time = int(time.time()) - 120

    while True:
        # Request for new mails every 120 seconds
        if int(time.time()) >= reference_time + 120:
            MAIL = imap.init_imap()
            reference_time = int(time.time())
        else:
            MAIL = False

        # Request for new images on Owncloud
        OWNCLOUD = oc.download_file()

        # If new images received by mail or Owncloud restart the slideshow with the new images
        if MAIL or OWNCLOUD:
            frame.restart_slideshow()

        # Request for new Telegram message
        TELEGRAM = tg.process_new_message()

        # If new images received by Telegram restart the slideshow with the new images
        if TELEGRAM:
            frame.restart_slideshow(static_variables.verbose)
