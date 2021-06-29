import os
import subprocess
import time
from imap import ImapMail
from frame import Frame
from telegram import Telegram
import module_log
import glob
import pathlib
import static_variables
import RPi.GPIO as GPIO
import texts


GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(9, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def tg_run():
    try:
        # Build up base parameters
        table = "telegram_bot"
        success = False

        # Get the last requested id and read the latest messages the latest messages
        offset = tg.get_last_update_id(table)
        answer = tg.read_message(offset=offset)

        # answer must not be a str
        if type(answer) != "str":
            for message in answer['result']:
                from_id = message['message']['from']['id']
                if from_id in tg.allowed_senders:
                    # only allow specific senders to send a photo to the frame
                    module_log.log("Message: " + str(message['message']))
                    if "photo" in message['message']:
                        # If user sent a photo
                        file, filename = tg.process_photo_name(message)

                        if tg.download_file(file, filename):
                            # If download of the sent photo is successfully reply to it
                            tg.send_message(from_id, f"{texts.de_telegram['thanks_image_upload']}")
                            success = True
                    elif "text" in message['message'] and from_id in tg.allowed_admins:
                        # If user sent text
                        success = tg.process_admin_commands(message)

                    #elif 'document' in message['message']:
                        # If user sent photo as a document
                    #    module_log.log("Document: " + str(message['message']['document']))
                else:
                    # If no allowed sender was found in config
                    module_log.log(f"Sender not allowed to send photos. ID: {from_id}")
                    tg.send_message(from_id, f"{texts.de_telegram['sender_not_allowed']} ID: {from_id}")

                tg.set_last_update_id(message['update_id'] + 1, table)
                tg.db_commit()

            return success

        else:
            return False

    except TypeError as e:
        print("TypeError: ", e)
    except KeyboardInterrupt:
        # Terminate the script
        print("Press Ctrl-C to terminate while statement")
    finally:
        #db_connection.commit()
        #db_connection.close()
        tg.db_close()


if __name__ == "__main__":
    frame = Frame(static_variables.timer, static_variables.blend, static_variables.photocount)
    imap = ImapMail(static_variables.EMAIL_ACCOUNT, static_variables.EMAIL_PASS, hostname=static_variables.EMAIL_HOST, ext=static_variables.file_extensions)
    tg = Telegram(static_variables.token, static_variables.tg_allowed_senders, static_variables.tg_allowed_admins)
    tg.set_commands()

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

