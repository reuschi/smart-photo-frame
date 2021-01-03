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


token = static_variables.token
allowed_senders = static_variables.tg_allowed_senders
weblink = f"https://api.telegram.org/bot{token}/"
filelink = f"https://api.telegram.org/file/bot{token}/"
http = urllib3.PoolManager()
db_connection = None


def telegram_POST(link, data={}):
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
        status_code = "Unknown exception: {}".format(e)
        module_log.log(status_code)
    finally:
        return return_Status_Code(answer)


def telegram_GET(link, data):
    answer = requests.Response()
    try:
        answer = requests.get(link, params=data)
        return return_Status_Code(answer)
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
        status_code = "Unknown exception: {}".format(e)
        module_log.log(status_code)
    finally:
        return return_Status_Code(answer)


def read_Message(**kwargs):
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
    try:
        file = pathlib.Path(pathlib.Path(__file__).parent.absolute() / destination / filename)

        url = filelink + source

        with http.request('GET', source, preload_content=False) as r, open(file, 'wb') as out_file:
            shutil.copyfileobj(r, out_file)

        return True
    except Exception as e:
        module_log.log(e)
    except IOError as e:
        module_log.log("Unable to download file.")

    return False


def print_Content(answer):
    content = answer.json()
    module_log.log(content['result'].keys())


def send_Message(chat_id, message):
    link = weblink + "sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message
    }
    return telegram_POST(link, data)


def send_Photo(chat_id, photo):
    link = weblink + "sendPhoto"
    data = {
        "chat_id": chat_id,
        "photo": photo
    }

    return telegram_POST(link, data)


def set_Last_Update_Id(update_id, table):
    try:
        c = db_connection.cursor()
        module_log.log("Setting last update id in database...")

        if update_id is None:
            module_log.log("ID is None")
            update_id = 0

        c.execute("""CREATE TABLE IF NOT EXISTS {} (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    last_update_id
                                )""".format(table))

        for row in c.execute("SELECT EXISTS (SELECT last_update_id FROM telegram_bot WHERE id=1)"):
            if row[0] == 1:
                c.execute("UPDATE telegram_bot SET last_update_id='{}' WHERE id=1".format(update_id))
                module_log.log("DB Update successful! ID: {}".format(update_id))
            else:
                c.execute("INSERT INTO {} (last_update_id) VALUES ({})".format(table, update_id))
                module_log.log("DB Insert successful! ID: {}".format(update_id))

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
    try:
        c = db_connection.cursor()
        module_log.log("Getting last update id from database...")

        for row in c.execute("SELECT last_update_id FROM telegram_bot WHERE id=1"):
            id = row[0]

        if id is not None:
            module_log.log(f"Done. Last Update ID is: {id}")
            return id

    except sqlite3.Error as e:
        module_log.log(e)
        module_log.log("SQLite3.Error")
    except sqlite3.OperationalError as e:
        module_log.log(e)
        module_log.log("SQLite3.OperationalError")
        set_Last_Update_Id(0, table)
    else:
        #module_log.log(sys.exc_info()[0] + ": " + sys.exc_info()[1])
        module_log.log("Failed!")
        return False


def main():
    global db_connection
    try:

        table = "telegram_bot"
        success = False

        db_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "telegram_bot.db")
        db_connection = sqlite3.connect(db_path)
        offset = get_Last_Update_Id(table)
        answer = read_Message(offset=offset)

        if type(answer) != 'str':
            for message in answer['result']:
                id = message['message']['from']['id']
                #if 'text' in message['message']:
                #    module_log.log("Text: " + str(message['message']['text']))
                #    if message['message']['text'] == "/help":
                #        send_Message(id, "/help - Zeige diese Hilfe an\n/batman - Ich zeige dir, wer Batman ist!\n/batsignal - Rufe Batman""")
                #    elif message['message']['text'] == "/batman":
                #        send_Message(id, "Ich bin Batman!")
                #        module_log.log("Batman")
                #    elif message['message']['text'] == "/batsignal":
                #        file = "https://upload.wikimedia.org/wikipedia/en/c/c6/Bat-signal_1989_film.jpg"
                #        send_Photo(id, file)
                #        module_log.log("Batsignal")
                    # success = True
                #elif 'document' in message['message']:
                #    module_log.log("Document: " + str(message['message']['document']))
                if 'photo' in message['message']:
                    module_log.log("Photo: " + str(message['message']))
                    if message['message']['from']['id'] in allowed_senders:
                        # only allow specific senders to send a photo to the frame
                        file = get_File_Link(message['message']['photo'][-1]['file_id'])
                        extension = file.split(".")[-1]
                        if 'caption' in message['message']:
                            # reformat the caption to use it as filename
                            caption = message['message']['caption']
                            caption = caption.replace(" ", "_")
                            caption = caption.replace("/", "_")
                            caption = caption.replace("\\", "_")
                            caption = caption.replace("*", "-")
                            filename = caption + "_tg." + extension
                        else:
                            filename = time.strftime("%Y%m%d_%H%M%S") + "_tg." + extension

                        if download_File(file, filename):
                            send_Message(id, "Danke für das Bild. Ich habe es für die Verwendung in der Datenbank gespeichert und die Präsentation neu gestartet.")
                            success = True
                    else:
                        module_log.log("Sender not allowed to send pictures. ID: {}".format(message['message']['from']['id']))

                module_log.log(message['update_id'])
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