from dbhelper import DBHelper
from image_processing import IProc
import requests
import time
import urllib3
import shutil
import module_log
import pathlib
import static_variables
import subprocess
import texts
import json
import git
import sys


class Telegram:

    def __init__(self, token: str, allowed_senders: list, allowed_admins: list):
        self.token = token
        self.allowed_senders = allowed_senders
        self.allowed_admins = allowed_admins
        self.weblink = f"https://api.telegram.org/bot{token}/"
        self.filelink = f"https://api.telegram.org/file/bot{token}/"
        self.http = urllib3.PoolManager()
        self.language = static_variables.language
        self.status_signal = static_variables.status_signal
        self.timeout = static_variables.poll_timeout
        self.db = DBHelper("telegram_bot")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close_connection()

    def telegram_POST(self, link, data={}, file=None) -> dict:
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

    def set_webhook(self, url: str, **kwargs):
        # Set Telegram webhook
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
        # If signaling is activated, send signal
        if self.status_signal:
            # Send signal only to first admin
            self.send_message(static_variables.tg_allowed_admins[0], texts.texts[self.language]['tg']['snd_signal'])
            module_log.log("Signaling sent")

    def get_file_link(self, file_id) -> str:
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

    def download_file(self, source, filename: str, destination: str = "images"):
        # Download the image from the Telegram servers
        try:
            # Build the correct file path on the local file system
            file = pathlib.Path(pathlib.Path(__file__).parent.absolute() / destination / filename)
            file.parent.mkdir(exist_ok=True, parents=True)

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

    def send_message(self, chat_id: int, message, reply_to_message_id: int = None):
        # Send a message back to a chat_id
        link = self.weblink + "sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message
        }

        if reply_to_message_id:
            data['reply_to_message_id'] = reply_to_message_id

        return self.telegram_POST(link, data)

    def send_photo(self, chat_id: int, photo):
        # Send a photo as a reply
        link = self.weblink + "sendPhoto"
        data = {
            "chat_id": chat_id,
            "photo": photo
        }

        return self.telegram_POST(link, data)

    def send_file(self, chat_id: int, file):
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

    def replace_special_signs(self, input_text: str):
        # Replace special signs in comment to store it as file name
        text = input_text.replace(" ", "_")
        text = text.replace("/", "_")
        text = text.replace("\\", "_")
        text = text.replace("*", "-")
        text = text.replace(".", "_")
        text = text.replace("ß", "ss")

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

    def _add_file_extension(self, from_id, message_text):
        # Add a new file extension to allowed extension list
        extension = message_text.split(" ")[1:]

        for ext in extension:
            ext = ext.replace(".", "")
            static_variables.add_value_to_config("gmail", "file_extensions", ext)

        self.send_message(from_id, texts.texts[self.language]['tg']['new_file_extension'].format(extension))
        module_log.log(f"New extension(s) added: {extension}")

    def _add_sender(self, from_id, message_text):
        # Add a new id to allowed sender list
        add_id = message_text.split(" ")

        static_variables.add_value_to_config("telegram", "allowedsenders", add_id[1])
        self.allowed_senders.append(int(add_id[1]))
        self.send_message(from_id, texts.texts[self.language]['tg']['new_sender_id'].format(add_id[1]))
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
            files = [x.name for x in path.glob('**/*') if x.is_file()]
            self.send_message(from_id, str(files))
            module_log.log(f"Image listing sent.")
        except FileNotFoundError:
            self.send_message(from_id, "No image uploaded yet")
            module_log.log(f"Image folder not yet created")

    def _delete_images(self, from_id, message_text):
        # Delete images from disk
        success = False

        images = message_text.split(" ")[1:]
        for img in images:
            #image_file = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "images" / img)
            #bash_command = f"sudo rm {image_file}"
            #reply = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #stdout, stderr = reply.communicate()
            #encoding = 'utf-8'
            error = IProc.delete_image(img)
            if error == "":
                self.send_message(from_id, texts.texts[self.language]['tg']['id_delete_success'].format(img))
                module_log.log(f"{img} deleted.")
                success = True
            else:
                self.send_message(from_id, str(error))
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

    def _system_reboot(self, from_id, update_id):
        # Reboot system by shell command

        try:
            self.db.set_last_update_id(update_id + 1)
            self.db.commit()

            bash_command = f"sudo reboot"
            reply = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = reply.communicate()
            encoding = 'utf-8'
            if str(stderr, encoding) == "":
                module_log.log(f"Reboot initiated")
            else:
                self.send_message(from_id, texts.texts[self.language]['tg']['no_reboot_possible'])
                module_log.log(f"Error while rebooting")
        except Exception as e:
            module_log.log(e)

    def _system_update(self, from_id, message_text):
        # Update system to current version from GitHub repository
        success = False

        try:
            branch = message_text.split(" ")[1]
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

    def _toggle_signaling(self, from_id):
        # Switch status signaling
        if static_variables.status_signal:
            static_variables.status_signal = False
            static_variables.change_config_value('telegram', 'status_signal', 'False')
            self.send_message(from_id, texts.texts[self.language]['tg']['sw_signaling'].format("Off"))
            module_log.log("Status signaling set to Off")
        else:
            static_variables.status_signal = True
            static_variables.change_config_value('telegram', 'status_signal', 'True')
            self.send_message(from_id, texts.texts[self.language]['tg']['sw_signaling'].format("On"))
            module_log.log("Status signaling set to On")

    def _rotate(self, from_id, message_text):
        # Rotate images 90 degrees left or right
        success = False
        rotate = False

        try:
            file = message_text.split()

            for i in range(1, len(file)):
                filename = str(file[i].split(",")[0])
                rotation = str(file[i].split(",")[1])

                '''
                if rotation == "r":
                    rotate = IProc.rotate_right(filename)
                    #module_log.log(f"Image {filename} rotated right.")
                elif rotation == "l":
                    rotate = IProc.rotate_left(filename)
                    #module_log.log(f"Image {filename} rotated left.")
                '''
                result = IProc.rotate(filename, rotation)
                if result.startswith("Ok"):
                    self.send_message(from_id, texts.texts[self.language]['tg']['rotate_image_success'].format(filename))
                    success = True
                    rotate = False
                else:
                    self.send_message(from_id, texts.texts[self.language]['tg']['rotate_image_fail'].format(result))

        except Exception as e:
            module_log.log(e)
        finally:
            return success

    def _toggle_verbose(self, from_id):
        # Toggle verbose view of image show
        if not static_variables.verbose:
            static_variables.verbose = True
            self.send_message(from_id, texts.texts[self.language]['tg']['toggle_verbose'].format("On"))
            module_log.log(texts.texts['EN']['tg']['toggle_verbose'].format("On"))
        else:
            static_variables.verbose = False
            self.send_message(from_id, texts.texts[self.language]['tg']['toggle_verbose'].format("Off"))
            module_log.log(texts.texts['EN']['tg']['toggle_verbose'].format("Off"))
        return True

    def process_admin_commands(self, message):
        success = False
        from_id = message['message']['from']['id']
        message_text = message['message']['text']
        update_id = message['update_id']

        if message_text.startswith("/addsender"):
            # Add new senders into the config file
            self._add_sender(from_id, message_text)
        elif message_text.startswith("/addextension"):
            # Add new extension(s) to the allowed list and restart the frame afterwards
            self._add_file_extension(from_id, message_text)
        elif message_text == "/getident":
            # Get current external ip address
            self._get_identity(from_id)
        elif message_text == "/listimg":
            # List all images stored on frame
            self._list_images(from_id)
        elif message_text.startswith("/deleteimg"):
            # Delete images from frame and restart presentation
            success = self._delete_images(from_id, message_text)
        elif message_text == "/getlog":
            # Send log file as attachment
            self._send_log(from_id)
        elif message_text == "/getconfig":
            # Send configuration file as attachment
            self._send_config(from_id)
        elif message_text == "/reboot":
            # Reboot whole system
            self._system_reboot(from_id, update_id)
        elif message_text.startswith("/update"):
            # Update system with current repository and restart with new code
            success = self._system_update(from_id, message_text)
        elif message_text == "/toggle_signaling":
            # Switch the signaling return via Telegram when system boots up
            self._toggle_signaling(from_id)
        elif message_text.startswith("/rotate"):
            # Rotate image 90 degrees left or right
            success = self._rotate(from_id, message_text)
        elif message_text == "/toggle_verbose":
            # Toggle between "verbose" and "non verbose" in frame view
            success = self._toggle_verbose(from_id)

        return success

    def process_new_message(self):
        try:
            success = False

            # Get the last requested id and read the latest messages
            offset = self.db.get_last_update_id()
            answer = self.read_message(offset=offset, timeout=self.timeout)

            # Answer must not be a str
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
                            self.send_message(from_id, texts.texts[self.language]['tg']['thanks_image_upload'], message['message']['message_id'])
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
                    self.send_message(from_id, texts.texts[self.language]['tg']['sender_not_allowed'].format(from_id))

                self.db.set_last_update_id(message['update_id'] + 1)
                self.db.commit()

            return success

        except KeyboardInterrupt:
            # Terminate the script
            module_log.log("Script interrupted by terminal input")
            sys.exit(1)
        except TypeError as e:
            module_log.log("TypeError: " + str(e))

