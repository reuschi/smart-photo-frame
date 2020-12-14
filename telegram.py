import requests
import json
import time
import urllib3
import shutil
import sqlite3
import module_log
import pathlib


token = "1290167159:AAGPAeuCiln78_O4nYA0WBE1Wq9PhQT_RDg"
weblink = f"https://api.telegram.org/bot{token}/"
filelink = f"https://api.telegram.org/file/bot{token}/"
http = urllib3.PoolManager()
#offset = 0
db_connection = ""


def telegram_POST(link, data=""):
    try:
        answer = requests.post(link, data=data)
    except requests.exceptions.ConnectionError:
        answer.status_code = "Connection refused"

    return return_Status_Code(answer)


def telegram_GET(link, data):
    try:
        answer = requests.get(link, params=data)
    except requests.exceptions.ConnectionError:
        answer.status_code = "Connection refused"

    return return_Status_Code(answer)


def read_Message(**kwargs):
    try:
        link = weblink + "getUpdates"
        data = {}

        for key, value in kwargs.items():
            data[key] = value

    except Exception as e:
        module_log.log(e)

    return telegram_POST(link, data)


def return_Status_Code(answer):

    if answer.status_code == 200:
        #reply = answer.json()
        #return json.dumps(reply, indent=2)
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
        return "Unknown Error!" + str(answer)


def set_Webhook(url, **kwargs):
    link = weblink + "setWebhook"
    data = {
        'url': url
    }

    for key, value in kwargs.items():
        data[key] = value


def get_File_Link(id):
    try:
        link = weblink + "getFile"
        data = {
            'file_id': id
        }

        #for key, value in kwargs.items():
        #    data[key] = value

        file_json = telegram_POST(link, data)
        #print(file_json['result']['file_path'])
    except Exception as e:
        module_log.log(e)

    return filelink + file_json['result']['file_path']


def download_File(source, filename, destination="images"):
    try:
        file = pathlib.Path(pathlib.Path(__file__).parent.absolute() / destination / filename)

        url = filelink + source
        #http = urllib3.PoolManager()

        with http.request('GET', source, preload_content=False) as r, open(file, 'wb') as out_file:
            shutil.copyfileobj(r, out_file)
        #urllib.request.urlretrieve(source, destination + filename)
        return True
    except Exception as e:
        module_log.log(e)
        return False
    except IOError as e:
        module_log.log("Unable to download file.")
        return False


def print_Content(answer):
    content = answer.json()
    #data = json.loads(content)
    module_log.log(content['result'].keys())


def send_Message(chat_id, message):
    try:
        link = weblink + "sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message
        }
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        #message = requests.post(url, params=data)
        return telegram_POST(link, data)
        #print(message)
    except Exception as e:
        module_log.log(e)


def send_Photo(chat_id, photo):
    try:
        link = weblink + "sendPhoto"
        data = {
            "chat_id": chat_id,
            "photo": photo
        }

        return telegram_POST(link, data)

    except Exception as e:
        module_log.log(e)


def set_Last_Update_Id(id, table):
    #global db_connection
    try:
        c = db_connection.cursor()

        if id == None:
            module_log.log("ID is None")
            id = 0

        c.execute("""CREATE TABLE IF NOT EXISTS {} (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    last_update_id
                                )""".format(table))

        #last_update_id = c.execute("SELECT * FROM telegram_bot")
        #print(c.execute("SELECT EXISTS (SELECT last_update_id FROM telegram_bot WHERE id=1)"))
        for row in c.execute("SELECT EXISTS (SELECT last_update_id FROM telegram_bot WHERE id=1)"):
            if row[0] == 1:
                c.execute("UPDATE telegram_bot SET last_update_id='{}' WHERE id=1".format(id))
                module_log.log("DB Update")
            else:
                c.execute("INSERT INTO {} (last_update_id) VALUES ({})".format(table, id))
                module_log.log("DB Insert")
            #print("Eintrag 0: {}".format(row[1]))
    #    if c.execute("SELECT EXISTS (SELECT last_update_id FROM telegram_bot WHERE id=1)"):
        #c.execute("UPDATE telegram_bot SET last_update_id='{}' WHERE id=1".format(id))
    #    else:
        #c.execute("INSERT OR REPLACE INTO {} (last_update_id) VALUES ({})".format(table, id))
        db_connection.commit()

        module_log.log("Id: {}".format(id))

    except sqlite3.Error as e:
        module_log.log(e)


def get_Last_Update_Id(table):
    #global db_connection
    try:
        c = db_connection.cursor()
        module_log.log("get_Last_Update_Id")

        for row in c.execute("SELECT last_update_id FROM telegram_bot WHERE id=1"):
            id = row[0]

        #db_connection.commit()

        if id != None:
            return id
        else:
            return 0

    except sqlite3.Error as e:
        module_log.log(type(e))
        return 0
    except sqlite3.OperationalError as e:
        module_log.log(type(e))
        #if 'no such table' in e:
        #    print("Keine Tabelle gefunden" + e)

def main():
    try:
        global db_connection
        db_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "telegram_bot.db")
        db_connection = sqlite3.connect(db_path)
        table = "telegram_bot"

        offset = get_Last_Update_Id(table)
        module_log.log("Telegram offset: {}".format(offset))
        answer = read_Message(offset=offset)

        #print(json.dumps(answer, indent=2))

        for message in answer['result']:
            id = message['message']['from']['id']
            if 'text' in message['message']:
                module_log.log("Text: " + str(message['message']['text']))
                if message['message']['text'] == "/help":
                    send_Message(id, "/help - Zeige diese Hilfe an\n/batman - Ich Zeige dir, wer Batman ist!\n/batsignal - Rufe Batman""")
                elif message['message']['text'] == "/batman":
                    send_Message(id, "Ich bin Batman!")
                    module_log.log("Batman")
                elif message['message']['text'] == "/batsignal":
                    file = "https://upload.wikimedia.org/wikipedia/en/c/c6/Bat-signal_1989_film.jpg"
                    send_Photo(id, file)
                    module_log.log("Batsignal")
                module_log.log(message)
            elif 'document' in message['message']:
                module_log.log("Document: " + str(message['message']['document']))
            elif 'photo' in message['message']:
                module_log.log("Photo: " + str(message['message']))
                #print("ID: " + str(message['message']['photo'][0]['file_id']))
                file = get_File_Link(message['message']['photo'][2]['file_id'])
                extension = file.split(".")[-1]
                #print(extension)
                if 'caption' in message['message']:
                    caption = message['message']['caption']
                    caption = caption.replace(" ", "_")
                    caption = caption.replace("/", "_")
                    caption = caption.replace("\\", "_")
                    filename = caption + "_tg" + extension
                else:
                    filename = time.strftime("%Y%m%d_%H%M%S") + "_tg." + extension

                if download_File(file, filename) == True:
                    send_Message(id, "Danke für das Bild. Ich habe es für die Verwendung in der Datenbank gespeichert.")

                #print(filename)
                module_log.log(message['update_id'])
                set_Last_Update_Id(message['update_id'] + 1, table)
                db_connection.commit()
                return filename

            #set_Last_Update_Id(message['update_id'] + 1, table)
            #db_connection.commit()


        #time.sleep(5)

    except KeyboardInterrupt:
        # Terminate the script and switch off all leds
        print("Press Ctrl-C to terminate while statement")
        db_connection.commit()
        #db_connection.close()

    db_connection.commit()
    db_connection.close()


if __name__ == "__main__":
    main()