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


class Telegram:

    def __init__(self, token: str, allowed_senders: list, allowed_admins: list):
        self.token = token
        self.allowed_senders = allowed_senders
        self.allowed_admins = allowed_admins
        self.weblink = f"https://api.telegram.org/bot{token}/"
        self.filelink = f"https://api.telegram.org/file/bot{token}/"
        self.http = urllib3.PoolManager()
        db_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "telegram_bot.db")
        self.db_connection = sqlite3.connect(db_path)
        self.db_cursor = self.db_connection.cursor()
        self.table = "telegram_bot"

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

    def db_commit(self):
        self.db_connection.commit()

    def db_close(self):
        self.db_connection.commit()
        self.db_connection.close()

    def read_message(self, **kwargs):
        # Get new arrived messages since last Update receive
        link = self.weblink + "getUpdates"
        data = {}

        for key, value in kwargs.items():
            data[key] = value

        return self.telegram_POST(link, data)

    def return_status_code(self, answer):
        if answer.status_code == 200:
            return answer.json()
        elif answer.status_code == 400:
            return "400 - Bad Request!"
        elif answer.status_code == 401:
            return "401 - You're not authorized!"
        elif answer.status_code == 403:
            return "403 - Action is Forbidden!"
        elif answer.status_code == 404:
            return "404 - Request not found"
        elif answer.status_code == 406:
            return "406 - Request not acceptable"
        elif answer.status_code == 420:
            return "420 - The maximum allowed number of attempts to invoke the given method with the given input parameters has been exceeded."
        elif answer.status_code == 500:
            return "500 - An internal server error occurred while a request was being processed"
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

        return self.telegram_POST(link, data)

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

            url = self.filelink + source

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

    def set_last_update_id(self, update_id, table):
        # To set last requested message id in the database
        try:
            # Build up the database connection and set the cursor to the current database
            module_log.log("Setting last update id in database...")

            if update_id is None:
                module_log.log("ID is None")
                update_id = 0

            # If there is no table in the database then create it first
            self.db_cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table} (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        last_update_id
                                    )""")

            # Write the last update id into the database. If the value already exists just update the value of the field
            for row in self.db_cursor.execute("SELECT EXISTS (SELECT last_update_id FROM telegram_bot WHERE id=1)"):
                if row[0] == 1:
                    self.db_cursor.execute(f"UPDATE telegram_bot SET last_update_id='{update_id}' WHERE id=1")
                    module_log.log(f"DB Update successful! ID: {update_id}")
                else:
                    self.db_cursor.execute(f"INSERT INTO {table} (last_update_id) VALUES ({update_id})")
                    module_log.log(f"DB Insert successful! ID: {update_id}")

            return True

        except sqlite3.Error as e:
            module_log.log(e)
        except Exception as e:
            module_log.log(sys.exc_info()[0] + ": " + sys.exc_info()[1])
        finally:
            self.db_connection.commit()

        module_log.log("Setting last Update id was not possible.")
        return False

    def get_last_update_id(self, table):
        # To only receive the newest message since the last request it's necessary to send an offset id in the request.
        # This information is stored in the database and will be gathered by this function.
        try:
            module_log.log("Getting last update id from database...")
            id = None

            # Get last update id from database
            for row in self.db_cursor.execute("SELECT last_update_id FROM telegram_bot WHERE id=1"):
                id = row[0]

            if id is not None:
                module_log.log(f"Done. Last Update ID is: {id}")
                return id

        except sqlite3.Error as e:
            module_log.log(e)
            if "no such table" in str(e):
                self.set_last_update_id(0, table)
        except sqlite3.OperationalError as e:
            module_log.log(e)
        else:
            module_log.log("Failed!")
            return False

    def replace_special_signs(self, input_text: str):
        text = input_text.replace(" ", "_")
        text = text.replace("/", "_")
        text = text.replace("\\", "_")
        text = text.replace("*", "-")

        return text

    def process_photo_name(self, message):
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
        extension = message['message']['text'].split(" ")[1:]
        from_id = message['message']['from']['id']

        for ext in extension:
            ext = ext.replace(".", "")
            static_variables.add_value_to_config("gmail", "file_extensions", ext)
        self.send_message(from_id, "Neue Extension(s) aufgenommen.")
        module_log.log(f"New extension(s) added: {extension}")

    def _add_sender(self, message):
        add_id = message['message']['text'].split(" ")
        from_id = message['message']['from']['id']

        static_variables.add_value_to_config("telegram", "allowedsenders", add_id[1])
        self.allowed_senders.append(int(add_id[1]))
        self.send_message(from_id, "Neue ID ist aufgenommen.")
        module_log.log(f"New sender added to allowed sender list: {add_id[1]}")

    def _get_identity(self, message):
        from_id = message['message']['from']['id']

        ip = requests.get("https://api.ipify.org").text
        self.send_message(from_id, ip)
        module_log.log(f"Request for Identity. Identity is: {ip}")

    def _list_images(self, message):
        from_id = message['message']['from']['id']

        path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "images")
        files = os.listdir(path)
        self.send_message(from_id, str(files))
        module_log.log(f"Image listing sent.")

    def _delete_images(self, message, success):
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
                self.send_message(from_id, f"{img} erfolgreich gelöscht")
                module_log.log(f"{img} deleted.")
                success = True
            else:
                self.send_message(from_id, str(stderr, encoding))
                module_log.log(f"No image file deleted.")

        return success

    def _send_log(self, message):
        from_id = message['message']['from']['id']

        file = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "message.log")
        if self.send_file(from_id, file):
            module_log.log(f"Log File sent.")

    def _send_config(self, message):
        from_id = message['message']['from']['id']

        file = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "config.ini")
        if self.send_file(from_id, file):
            module_log.log(f"Configuration File sent.")

    def _system_reboot(self):
        bash_command = f"sudo reboot"
        reply = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = reply.communicate()
        module_log.log(f"Reboot initiated")

    def process_admin_commands(self, message):
        success = False

        if message['message']['text'].startswith("/addsender"):
            # Add new senders into the config file
            self._add_sender(message)
        elif message['message']['text'].startswith("/addextension"):
            # Add new extension(s) to the allowed list and restart the frame afterwards
            self._add_file_extension(message)
        elif message['message']['text'] == "/getident":
            # Get current external ip address
            self._get_identity(message)
        elif message['message']['text'] == "/listimg":
            # List all images stored on frame
            self._list_images(message)
        elif message['message']['text'].startswith("/deleteimg"):
            # Delete images from frame and restart presentation
            success = self._delete_images(message, success)
        elif message['message']['text'] == "/getlog":
            # Send log file as attachment
            self._send_log(message)
        elif message['message']['text'] == "/getconfig":
            # Send configuration file as attachment
            self._send_config(message)
        elif message['message']['text'] == "/reboot":
            # Reboot whole system
            self._system_reboot()

        return success

    def process_new_message(self):
        try:
            success = False

            # Get the last requested id and read the latest messages the latest messages
            offset = self.get_last_update_id(self.table)
            answer = self.read_message(offset=offset)

            # answer must not be a str
            #if type(answer) != "str":
            for message in answer['result']:
                from_id = message['message']['from']['id']
                if from_id in self.allowed_senders:
                    # only allow specific senders to send a photo to the frame
                    module_log.log("Message: " + str(message['message']))
                    if "photo" in message['message']:
                        # If user sent a photo
                        file, filename = self.process_photo_name(message)

                        if self.download_file(file, filename):
                            # If download of the sent photo is successfully reply to it
                            self.send_message(from_id, f"{texts.de_telegram['thanks_image_upload']}")
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
                    self.send_message(from_id, f"{texts.de_telegram['sender_not_allowed']} ID: {from_id}")

                self.set_last_update_id(message['update_id'] + 1, self.table)
                self.db_commit()

            return success

            #else:
            #    return False

        except TypeError as e:
            print("TypeError: ", e)
        except KeyboardInterrupt:
            # Terminate the script
            print("Press Ctrl-C to terminate while statement")
        #finally:
        #    self.db_close()
