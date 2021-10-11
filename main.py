import time
from imap import ImapMail
from frame import Frame
from telegram import Telegram
import module_log
import static_variables
import RPi.GPIO as GPIO
import texts


GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(9, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)


if __name__ == "__main__":
    frame = Frame(static_variables.timer, static_variables.blend, static_variables.photocount)
    imap = ImapMail(static_variables.EMAIL_ACCOUNT, static_variables.EMAIL_PASS, hostname=static_variables.EMAIL_HOST, ext=static_variables.file_extensions)
    tg = Telegram(static_variables.token, static_variables.tg_allowed_senders, static_variables.tg_allowed_admins)
    tg.set_commands()
    tg.send_signal()

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
            mail = imap.init_imap(static_variables.EMAIL_ACCOUNT, static_variables.EMAIL_PASS)
            i = 0
        else:
            i += 1
            mail = False

        # Request for new Telegram message
        telegram = tg.process_new_message()

        # If new images received by mail or Telegram restart the slideshow with the new images
        if telegram or mail:
            frame.restart_slideshow()

        time.sleep(15)

