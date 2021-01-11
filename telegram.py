import requests
import json
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


token = static_variables.token
allowed_senders = static_variables.tg_allowed_senders
weblink = f"https://api.telegram.org/bot{token}/"
filelink = f"https://api.telegram.org/file/bot{token}/"
http = urllib3.PoolManager()
db_connection = None


def telegram_POST(link, data={}):
    # Requesting Telegram API via POST Method
    answer = requests.Response()
    try:
        answer = requests.post(link, data=data)
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
        return return_Status_Code(answer)


def telegram_GET(link, data):
    # Requesting Telegram API via GET Method
    answer = requests.Response()
    try:
        answer = requests.get(link, params=data)
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
        return return_Status_Code(answer)


def read_Message(**kwargs):
    # Get new arrived messages since last Update receive
    link = weblink + "getUpdates"
    data = {}

    for key, value in kwargs.items():
        data[key] = value

    return telegram_POST(link, data)


def return_Status_Code(answer):
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


def set_Webhook(url, **kwargs):
    link = weblink + "setWebhook"
    data = {
        'url': url
    }

    for key, value in kwargs.items():
        data[key] = value


def get_File_Link(file_id):
    # To download a file it's necessary to get the direct link to the file
    try:
        link = weblink + "getFile"
        data = {
            'file_id': file_id
        }

        file_json = telegram_POST(link, data)

        return filelink + file_json['result']['file_path']
    except Exception as e:
        module_log.log(e)


def download_File(source, filename, destination="images"):
    # Download the image from the Telegram servers
    try:
        # Build the correct file path on the local file system
        file = pathlib.Path(pathlib.Path(__file__).parent.absolute() / destination / filename)

        url = filelink + source

        # Get the file downloaded
        with http.request('GET', source, preload_content=False) as r, open(file, 'wb') as out_file:
            shutil.copyfileobj(r, out_file)

        return True

    except IOError as e:
        module_log.log("Unable to download file.")
    except Exception as e:
        module_log.log(e)

    return False


def print_Content(answer):
    content = answer.json()
    module_log.log(content['result'].keys())


def send_Message(chat_id, message):
    # Send a message back to a chat_id
    link = weblink + "sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message
    }

    return telegram_POST(link, data)


def send_Photo(chat_id, photo):
    # Send a photo as a reply
    link = weblink + "sendPhoto"
    data = {
        "chat_id": chat_id,
        "photo": photo
    }

    return telegram_POST(link, data)


def set_Last_Update_Id(update_id, table):
    # To set last requested message id in the database
    try:
        # Build up the database connection and set the cursor to the current database
        c = db_connection.cursor()
        module_log.log("Setting last update id in database...")

        if update_id is None:
            module_log.log("ID is None")
            update_id = 0

        # If there is no table in the database then create it first
        c.execute(f"""CREATE TABLE IF NOT EXISTS {table} (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    last_update_id
                                )""")

        # Write the last update id into the database. If the value already exists just update the value of the field
        for row in c.execute("SELECT EXISTS (SELECT last_update_id FROM telegram_bot WHERE id=1)"):
            if row[0] == 1:
                c.execute(f"UPDATE telegram_bot SET last_update_id='{update_id}' WHERE id=1")
                module_log.log(f"DB Update successful! ID: {update_id}")
            else:
                c.execute(f"INSERT INTO {table} (last_update_id) VALUES ({update_id})")
                module_log.log(f"DB Insert successful! ID: {update_id}")

        return True

    except sqlite3.Error as e:
        module_log.log(e)
    except Exception as e:
        module_log.log(sys.exc_info()[0] + ": " + sys.exc_info()[1])
    finally:
        db_connection.commit()

    module_log.log("Setting last Update id was not possible.")
    return False


def get_Last_Update_Id(table):
    # To only receive the newest message since the last request it's necessary to send an offset id.
    # This information is stored in the database and will be gathered by this function.
    try:
        c = db_connection.cursor()
        module_log.log("Getting last update id from database...")

        # Get last update id from database
        for row in c.execute("SELECT last_update_id FROM telegram_bot WHERE id=1"):
            id = row[0]

        if id is not None:
            module_log.log(f"Done. Last Update ID is: {id}")
            return id

    except sqlite3.Error as e:
        module_log.log(e)
        if "no such table" in str(e):
            set_Last_Update_Id(0, table)
    except sqlite3.OperationalError as e:
        module_log.log(e)
    else:
        module_log.log("Failed!")
        return False


def main():
    global db_connection
    try:
        table = "telegram_bot"
        success = False

        # Build up database connection, get the last requested id and receive the latest messages
        db_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "telegram_bot.db")
        db_connection = sqlite3.connect(db_path)
        offset = get_Last_Update_Id(table)
        answer = read_Message(offset=offset)

        # answer must not be a str
        if type(answer) != 'str':
            for message in answer['result']:
                from_id = message['message']['from']['id']
                if from_id in allowed_senders:
                    # only allow specific senders to send a photo to the frame
                    module_log.log("Message: " + str(message['message']))
                    if 'photo' in message['message']:
                        # If user sent a photo
                        file = get_File_Link(message['message']['photo'][-1]['file_id'])
                        extension = file.split(".")[-1]
                        if 'caption' in message['message']:
                            # Reformat the caption of the image to use it as filename
                            caption = message['message']['caption']
                            caption = caption.replace(" ", "_")
                            caption = caption.replace("/", "_")
                            caption = caption.replace("\\", "_")
                            caption = caption.replace("*", "-")
                            filename = caption + "_tg." + extension
                        else:
                            # If no caption is set use the current date and time as filename
                            filename = time.strftime("%Y%m%d_%H%M%S") + "_tg." + extension

                        if download_File(file, filename):
                            # If download of the sent photo is successfully reply to it
                            send_Message(from_id, "Danke für das Bild. Ich habe es für die Verwendung in der Datenbank gespeichert und die Präsentation neu gestartet.")
                            success = True
                    elif 'text' in message['message']:
                        # If user sent text
                        if message['message']['text'].startswith("/addsender"):
                            # Add new senders into the config file
                            add_id = message['message']['text'].split(" ")
                            module_log.log(f"Adding new sender to allowed sender list: {add_id[1]}")
                            static_variables.add_Value_To_Config("telegram", "allowedsenders", add_id[1])
                            send_Message(from_id, "Neue ID ist aufgenommen.")
                            module_log.log("Done.")
                        elif message['message']['text'] == "/getident":
                            # Get current external ip address
                            ip = requests.get("https://api.ipify.org").text
                            send_Message(from_id, ip)
                            module_log.log(f"Request for Identity. Identity is: {ip}")
                        elif message['message']['text'] == "/listimg":
                            # List all images stored on frame
                            files = os.listdir("/home/pi/python/smart-photo-frame/images/")
                            send_Message(from_id, str(files))
                        elif message['message']['text'].startswith("/deleteimg"):
                            # Delete images from frame and restart presentation
                            images = message['message']['text'].split(" ")
                            for img in images:
                                if img != "/deleteimg":
                                    bashCommand = f"sudo rm /home/pi/python/smart-photo-frame/images/{img}"
                                    reply = subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                    stdout, stderr = reply.communicate()
                                    # os.system(f"sudo rm /home/pi/python/smart-photo-frame/images/{img}")
                                    print(stderr)
                                    print(stdout)
                                    if stderr is "b''":
                                        send_Message(from_id, f"{img} erfolgreich gelöscht")
                                        module_log.log(f"{img} deleted.")
                                        success = True
                                    else:
                                        send_Message(from_id, f"{stderr}")
                                        module_log.log(f"No image file deleted.")


                    #elif 'document' in message['message']:
                        # If user sent photo as a document
                    #    module_log.log("Document: " + str(message['message']['document']))
                else:
                    # If no allowed sender was found in config
                    module_log.log(f"Sender not allowed to send photos. ID: {from_id}")
                    send_Message(from_id, f"Not allowed! ID: {from_id}")

                set_Last_Update_Id(message['update_id'] + 1, table)
                db_connection.commit()

            return success

        else:
            return False

    except TypeError as e:
        print("TypeError: ", e)
    except KeyboardInterrupt:
        # Terminate the script
        print("Press Ctrl-C to terminate while statement")
        # db_connection.commit()
        # db_connection.close()
    finally:
        db_connection.commit()
        db_connection.close()


if __name__ == "__main__":
    main()