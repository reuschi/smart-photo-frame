""" Main file to start the Smart Photo Frame """

import time

from RPi import GPIO
from imap import ImapMail
from frame import Frame
from telegram import Telegram
from owncloud import Owncloud
import module_log
import static_variables as static


GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(9, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)


if __name__ == "__main__":
    frame = Frame(static.timer, static.blend, static.photocount)

    if hasattr(static, 'EMAIL_ACCOUNT'):
        imap = ImapMail(static.EMAIL_ACCOUNT, static.EMAIL_PASS,
                        static.EMAIL_HOST, static.file_extensions)

    if hasattr(static, 'oc_host'):
        oc = Owncloud(static.oc_host, static.oc_username,
                  static.oc_password)

    if hasattr(static, 'tg_token'):
        tg = Telegram(static.tg_token, static.tg_allowed_senders,
                      static.tg_allowed_admins)
        tg.set_commands()
        tg.send_signal()

    module_log.log("!!!! SYSTEM STARTED !!!!")
    frame.restart_slideshow(static.verbose)

    # Rise presentation Timer
    GPIO.add_event_detect(27, GPIO.FALLING, callback=frame.rise_timer, bouncetime=400)

    # Lower presentation Timer
    GPIO.add_event_detect(19, GPIO.FALLING, callback=frame.lower_timer, bouncetime=400)

    # Shutdown the system
    GPIO.add_event_detect(9, GPIO.FALLING, callback=frame.system_shutdown, bouncetime=400)

    # Set current time to 120 seconds in the past
    reference_time = int(time.time()) - 120

    OWNCLOUD = False
    MAIL = False
    TELEGRAM = False

    while True:
        # Request for new mails and new images on Owncloud every 120 seconds
        if int(time.time()) >= reference_time + 120:
            if hasattr(static, 'EMAIL_ACCOUNT'):
                MAIL = imap.init_imap()
            if hasattr(static, 'oc_host'):
                OWNCLOUD = oc.download_file()
            reference_time = int(time.time())
        else:
            MAIL = False
            OWNCLOUD = False

        # If new images received by mail or Owncloud restart the slideshow with the new images
        if MAIL or OWNCLOUD:
            frame.restart_slideshow()

        # Request for new Telegram message
        if hasattr(static, 'tg_token'):
            TELEGRAM = tg.process_new_message()

        # If new images received by Telegram restart the slideshow with the new images
        if TELEGRAM:
            frame.restart_slideshow(static.verbose)
