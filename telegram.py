from dbhelper import DBHelper
import requests
import time
import urllib3
import shutil
import sqlite3
import module_log
import pathlib
import static_variables
import sys
import os
import subprocess
import texts
import json
import git


class Telegram:

    def __init__(self, token: str, allowed_senders: list, allowed_admins: list):
        self.token = token
        self.allowed_senders = allowed_senders
        self.allowed_admins = allowed_admins
        self.weblink = f"https://api.telegram.org/bot{token}/"
        self.filelink = f"https://api.telegram.org/file/bot{token}/"
        self.http = urllib3.PoolManager()
        #db_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "telegram_bot.db")
        #self.db_connection = sqlite3.connect(db_path)
        #self.db_cursor = self.db_connection.cursor()
        #self.table = "telegram_bot"
        self.language = static_variables.language
        self.status_signal = static_variables.status_signal
        self.timeout = static_variables.poll_timeout
        self.db = DBHelper("telegram_bot")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close_connection()

    def telegram_POST(self, link, data={}, file=None):
        # Requesting Telegram API via POST Method
        answer = requests.Response()
        try:
            answer = requests.post(link, data=data, files=file)
        except requests.exceptions.ConnectionError:
            status_code = "Connection refused"
            module_log.log(status_code)
        except requests.exceptions.HTTPError:
            status_code = "Maximum retries reached"
            module_log.log(status_code)
        except requests.exceptions.RetryError:
            status_code = "No DNS available"
            module_log.log(status_code)
        except requests.exceptions as e:
            status_code = "Any other Exception from Requests has been raised"
            module_log.log(status_code)
            module_log.log(e)
        except Exception as e:
            status_code = f"Unknown exception: {e}"
            module_log.log(status_code)
        finally:
            return self.return_status_code(answer)

    #def db_commit(self):
    #    self.db_connection.commit()

    #def db_close(self):
    #    self.db_connection.commit()
    #    self.db_connection.close()

    def read_message(self, **kwargs):
        # Get new arrived messages since last Update receive
        link = self.weblink + "getUpdates"
        data = {}

        for key, value in kwargs.items():
            data[key] = value

        return self.telegram_POST(link, data)

    def return_status_code(self, answer):
        # Return a readable status code
        if answer.status_code == 200:
            return answer.json()
        elif answer.status_code == 400:
            return texts.texts[self.language]['tg']['return_400']
        elif answer.status_code == 401:
            return texts.texts[self.language]['tg']['return_401']
        elif answer.status_code == 403:
            return texts.texts[self.language]['tg']['return_403']
        elif answer.status_code == 404:
            return texts.texts[self.language]['tg']['return_404']
        elif answer.status_code == 406:
            return texts.texts[self.language]['tg']['return_406']
        elif answer.status_code == 420:
            return texts.texts[self.language]['tg']['return_420']
        elif answer.status_code == 500:
            return texts.texts[self.language]['tg']['return_500']
        else:
            return "Unknown Error! " + str(answer)

    def set_webhook(self, url, **kwargs):
        link = self.weblink + "setWebhook"
        data = {
            "url": url
        }

        for key, value in kwargs.items():
            data[key] = value

        return self.telegram_POST(link, data)

    def set_commands(self):
        # Set all commands defined in the config as shown commands in the bot
        link = self.weblink + "setMyCommands"
        data = {
            "commands": json.dumps(static_variables.tg_bot_commands)
        }
        module_log.log(data)
        return self.telegram_POST(link, data)

    def send_signal(self):
        print(self.status_signal)
        if self.status_signal:
            self.send_message("28068117", texts.texts[self.language]['tg']['snd_signal'])

    def get_file_link(self, file_id):
        # To download a file it's necessary to get the direct link to the file
        try:
            link = self.weblink + "getFile"
            data = {
                "file_id": file_id
            }

            file_json = self.telegram_POST(link, data)

            return self.filelink + file_json['result']['file_path']
        except Exception as e:
            module_log.log(e)

    def download_file(self, source, filename, destination="images"):
        # Download the image from the Telegram servers
        try:
            # Build the correct file path on the local file system
            file = pathlib.Path(pathlib.Path(__file__).parent.absolute() / destination / filename)
            file.parent.mkdir(exist_ok=True, parents=True)

            #url = self.filelink + source

            # Get the file downloaded
            with self.http.request("GET", source, preload_content=False) as r, open(file, "wb") as out_file:
                shutil.copyfileobj(r, out_file)

            return True

        except IOError as e:
            module_log.log("Unable to download file.")
        except Exception as e:
            module_log.log(e)

        return False

    def print_content(self, answer):
        content = answer.json()
        module_log.log(content['result'].keys())

    def send_message(self, chat_id, message):
        # Send a message back to a chat_id
        link = self.weblink + "sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message
        }

        return self.telegram_POST(link, data)

    def send_photo(self, chat_id, photo):
        # Send a photo as a reply
        link = self.weblink + "sendPhoto"
        data = {
            "chat_id": chat_id,
            "photo": photo
        }

        return self.telegram_POST(link, data)

    def send_file(self, chat_id, file):
        # Send a byte file as a reply
        link = self.weblink + "sendDocument"
        data = {
            "chat_id": chat_id
        }
        document = {
            "document": (str(file), open(str(file), "rb"))
        }

        return_value = self.telegram_POST(link, data, document)
        if return_value['result']['document'] != "":
            return True
        else:
            return False

    #def set_last_update_id(self, update_id, table):
        # To set last requested message id in the database
    #    try:
            # Build up the database connection and set the cursor to the current database
    #        module_log.log("Setting last update id in database...")

    #        if update_id is None:
    #            module_log.log("ID is None")
    #            update_id = 0

            # If there is no table in the database then create it first
    #        self.db.create_table(table)

            # Write the last update id into the database. If the value already exists just update the value of the field
    #        for row in self.db.select("SELECT EXISTS (SELECT last_update_id FROM telegram_bot WHERE id=1)"):
    #            if row[0] == 1:
    #                self.db.update_last_id(update_id)
    #                module_log.log(f"DB Update successful! ID: {update_id}")
    #            else:
    #                self.db.insert_last_id(update_id)
    #                module_log.log(f"DB Insert successful! ID: {update_id}")

    #        return True

    #    except sqlite3.Error as e:
    #        module_log.log(e)
    #    except Exception as e:
    #        module_log.log(sys.exc_info()[0] + ": " + sys.exc_info()[1])
    #    finally:
    #        self.db.commit()

    #    module_log.log("Setting last update id was not possible.")
    #    return False

    #def get_last_update_id(self, table):
        # To only receive the newest message since the last request it's necessary to send an offset id in the request.
        # This information is stored in the database and will be gathered by this function.
    #    try:
    #        module_log.log("Getting last update id from database...")
    #        update_id = None

            # Get last update id from database
    #        for row in self.db.select("SELECT last_update_id FROM telegram_bot WHERE id=1"):
    #            update_id = row[0]

    #        if update_id is not None:
    #            module_log.log(f"Done. Last Update ID is: {update_id}")
    #            return update_id

    #    except sqlite3.Error as e:
    #        module_log.log(e)
    #        if "no such table" in str(e):
    #            self.set_last_update_id(0, table)
    #    except sqlite3.OperationalError as e:
    #        module_log.log(e)
    #    else:
    #        module_log.log("Failed!")
    #        return False

    def replace_special_signs(self, input_text: str):
        # Replace special signs in comment to store it as file name
        text = input_text.replace(" ", "_")
        text = text.replace("/", "_")
        text = text.replace("\\", "_")
        text = text.replace("*", "-")

        return text

    def process_photo_name(self, message):
        # Rename image file if there is a comment added to the photo
        file = self.get_file_link(message['message']['photo'][-1]['file_id'])
        extension = file.split(".")[-1]
        if "caption" in message['message']:
            # Reformat the caption of the image to use it as filename
            caption = self.replace_special_signs(message['message']['caption'])
            filename = caption + "_tg." + extension
        else:
            # If no caption is set use the current date and time as filename
            filename = time.strftime("%Y%m%d_%H%M%S") + "_tg." + extension

        return file, filename

    def _add_file_extension(self, message):
        # Add a new file extension to allowed extension list
        extension = message['message']['text'].split(" ")[1:]
        from_id = message['message']['from']['id']

        for ext in extension:
            ext = ext.replace(".", "")
            static_variables.add_value_to_config("gmail", "file_extensions", ext)
        self.send_message(from_id, texts.texts[self.language]['tg']['new_file_extension'])
        module_log.log(f"New extension(s) added: {extension}")

    def _add_sender(self, message):
        # Add a new id to allowed sender list
        add_id = message['message']['text'].split(" ")
        from_id = message['message']['from']['id']

        static_variables.add_value_to_config("telegram", "allowedsenders", add_id[1])
        self.allowed_senders.append(int(add_id[1]))
        self.send_message(from_id, texts.texts[self.language]['tg']['new_sender_id'])
        module_log.log(f"New sender added to allowed sender list: {add_id[1]}")

    def _get_identity(self, from_id):
        # Return public ip address to sender
        ip = requests.get("https://api.ipify.org").text
        self.send_message(from_id, ip)
        module_log.log(f"Request for Identity. Identity is: {ip}")

    def _list_images(self, from_id):
        # List all images stored on the disk (in subfolder ./images)
        path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "images")
        try:
            #files = os.listdir(path)
            files = [x for x in p if x.is_file()]
            self.send_message(from_id, str(files))
            module_log.log(f"Image listing sent.")
        except FileNotFoundError:
            self.send_message(from_id, "No image uploaded yet")
            module_log.log(f"Image folder not yet created")

    def _delete_images(self, message, success):
        # Delete images from disk
        from_id = message['message']['from']['id']

        images = message['message']['text'].split(" ")[1:]
        # images.remove("/deleteimg")
        for img in images:
            image_file = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "images" / img)
            bashCommand = f"sudo rm {image_file}"
            reply = subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = reply.communicate()
            encoding = 'utf-8'
            if str(stderr, encoding) is "":
                self.send_message(from_id, f"{img} {texts.texts[self.language]['tg']['id_delete_success']}")
                module_log.log(f"{img} deleted.")
                success = True
            else:
                self.send_message(from_id, str(stderr, encoding))
                module_log.log(f"No image file deleted.")

        return success

    def _send_log(self, from_id):
        # Fetch log file and send it back to the user
        file = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "message.log")
        if self.send_file(from_id, file):
            module_log.log(f"Log File sent.")

    def _send_config(self, from_id):
        # Fetch config file and send it back to the user
        file = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "config.ini")
        if self.send_file(from_id, file):
            module_log.log(f"Configuration file sent.")

    def _system_reboot(self, from_id):
        # Reboot system by shell command
        bash_command = f"sudo reboot"
        reply = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = reply.communicate()
        encoding = 'utf-8'
        if str(stderr, encoding) is "":
            module_log.log(f"Reboot initiated")
        else:
            self.send_message(from_id, texts.texts[self.language]['tg']['no_reboot_possible'])
            module_log.log(f"Error while rebooting")

    def _system_update(self, message):
        # Update system to current version from GitHub repository
        from_id = message['message']['from']['id']
        success = False

        try:
            branch = message['message']['text'].split(" ")[1]
        except IndexError:
            branch = "master"

        module_log.log(f"Updating branch {branch}")
        repo = git.Repo('/home/pi/python/smart-photo-frame')
        repo.git.checkout(branch)
        update = repo.git.pull('origin', branch)
        if "Updating" in update:
            self.send_message(from_id, texts.texts[self.language]['tg']['sys_upd_success'])
            module_log.log(f"System update done")
            success = True
        elif "Already up to date" in update:
            self.send_message(from_id, texts.texts[self.language]['tg']['sys_upd_no_need'])
            module_log.log(f"System was up to date")
        else:
            self.send_message(from_id, texts.texts[self.language]['tg']['sys_upd_failed'])
            module_log.log(f"System update failed!")

        return success

    def _switch_signaling(self, from_id):
        # Switch status signaling
        if static_variables.status_signal:
            static_variables.status_signal = False
            static_variables.change_config_value('telegram', 'status_signal', 'False')
            self.send_message(from_id, texts.texts[self.language]['tg']['sw_signaling_false'])
            module_log.log("Status signaling set to Off")
        else:
            static_variables.status_signal = True
            static_variables.change_config_value('telegram', 'status_signal', 'True')
            self.send_message(from_id, texts.texts[self.language]['tg']['sw_signaling_true'])
            module_log.log("Status signaling set to On")

    def process_admin_commands(self, message):
        success = False
        from_id = message['message']['from']['id']

        if message['message']['text'].startswith("/addsender"):
            # Add new senders into the config file
            self._add_sender(message)
        elif message['message']['text'].startswith("/addextension"):
            # Add new extension(s) to the allowed list and restart the frame afterwards
            self._add_file_extension(message)
        elif message['message']['text'] == "/getident":
            # Get current external ip address
            self._get_identity(from_id)
        elif message['message']['text'] == "/listimg":
            # List all images stored on frame
            self._list_images(from_id)
        elif message['message']['text'].startswith("/deleteimg"):
            # Delete images from frame and restart presentation
            success = self._delete_images(message, success)
        elif message['message']['text'] == "/getlog":
            # Send log file as attachment
            self._send_log(from_id)
        elif message['message']['text'] == "/getconfig":
            # Send configuration file as attachment
            self._send_config(from_id)
        elif message['message']['text'] == "/reboot":
            # Reboot whole system
            self._system_reboot(from_id)
        elif message['message']['text'].startswith("/update"):
            # Update system with current repository and restart with new code
            success = self._system_update(message)
        elif message['message']['text'] == "/swsignaling":
            # Switch the signaling return via Telegram when system boots up
            self._switch_signaling(from_id)

        return success

    def process_new_message(self):
        try:
            success = False

            # Get the last requested id and read the latest messages
            offset = self.db.get_last_update_id()
            answer = self.read_message(offset=offset, timeout=self.timeout)

            # Answer must not be a str
            #if type(answer) != "str":
            for message in answer['result']:
                from_id = message['message']['from']['id']
                if from_id in self.allowed_senders:
                    # Only allow specific senders to send a photo to the frame
                    module_log.log("Message: " + str(message['message']))
                    if "photo" in message['message']:
                        # If user sent a photo
                        file, filename = self.process_photo_name(message)

                        if self.download_file(file, filename):
                            # If download of the sent photo is successfully reply to it
                            self.send_message(from_id, f"{texts.texts[self.language]['tg']['thanks_image_upload']}")
                            success = True
                    elif "text" in message['message'] and from_id in self.allowed_admins:
                        # If user sent text
                        success = self.process_admin_commands(message)

                    #elif 'document' in message['message']:
                        # If user sent photo as a document
                    #    module_log.log("Document: " + str(message['message']['document']))
                else:
                    # If no allowed sender was found in config
                    module_log.log(f"Sender not allowed to send photos. ID: {from_id}")
                    self.send_message(from_id, f"{texts.texts[self.language]['tg']['sender_not_allowed']} ID: {from_id}")

                self.db.set_last_update_id(message['update_id'] + 1)
                self.db.commit()

            return success

            #else:
            #    return False

        except TypeError as e:
            module_log.log("TypeError: ", e)
        except KeyboardInterrupt:
            # Terminate the script
            module_log.log("Script interrupted by terminal input")
        #finally:
        #    self.db_close()
