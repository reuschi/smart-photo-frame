import requests
import json
import time
import urllib3
import shutil
import sqlite3


token = "1290167159:AAGPAeuCiln78_O4nYA0WBE1Wq9PhQT_RDg"
weblink = f"https://api.telegram.org/bot{token}/"
filelink = f"https://api.telegram.org/file/bot{token}/"
http = urllib3.PoolManager()
#offset = 0
db_connection = sqlite3.connect("telegram_bot.db")

#with open(API_CODE) as file:
#    token = file.read()

def telegram_POST(link, data=""):
    answer = requests.post(link, data=data)

    return return_Status_Code(answer)


def telegram_GET(link, data):
    answer = requests.get(link, params=data)

    return return_Status_Code(answer)


def read_Message(**kwargs):
    link = weblink + "getUpdates"
    data = {}

    for key, value in kwargs.items():
        data[key] = value

    #answer = requests.post(link, data=data)
    #print(type(answer.status_code))
    #if answer.status_code == 200:
    #    new_answer = answer.json()
    #    print(new_answer['result'][0]['message']['text'])
    #    return answer

    return telegram_POST(link, data)


def return_Status_Code(answer):


    if answer.status_code == 200:
        reply = answer.json()
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
    link = weblink + "getFile"
    data = {
        'file_id': id
    }

    #for key, value in kwargs.items():
    #    data[key] = value

    file_json = telegram_POST(link, data)
    #print(file_json['result']['file_path'])
    return filelink + file_json['result']['file_path']


def download_File(source, filename, destination="images/"):
    url = filelink + source
    #http = urllib3.PoolManager()

    with http.request('GET', source, preload_content=False) as r, open(destination + filename, 'wb') as out_file:
        shutil.copyfileobj(r, out_file)
    #urllib.request.urlretrieve(source, destination + filename)


def print_Content(answer):
    content = answer.json()
    #data = json.loads(content)
    print(content['result'].keys())


def send_Message(chat_id, message):
    link = weblink + "sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message
    }
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    #message = requests.post(url, params=data)
    telegram_POST(link, data)
    #print(message)


def send_Photo(chat_id, photo):
    link = weblink + "sendPhoto"
    data = {
        "chat_id": chat_id,
        "photo": photo
    }

    return telegram_POST(link, data)


def set_Last_Update_Id(id, table):
    c = db_connection.cursor()

    if id == None:
        id = 0

    c.execute("""CREATE TABLE IF NOT EXISTS {} (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                last_update_id
                            )""".format(table))

    #last_update_id = c.execute("SELECT * FROM telegram_bot")
    try:
        c.execute("UPDATE telegram_bot SET last_update_id='{}' WHERE id=1".format(id))
        db_connection.commit()

        print("Id: {}".format(id))

    except sqlite3.Error as e:
        print(e)


def get_Last_Update_Id(table):
    c = db_connection.cursor()

    try:
        for row in c.execute("SELECT last_update_id FROM telegram_bot WHERE id=1"):
            id = row[0]

        db_connection.commit()

        if id != None:
            return id
        else:
            return 0

    except sqlite3.Error as e:
        print(e)


def main():
    table = "telegram_bot"

    try:
        while True:
            offset = get_Last_Update_Id(table)
            print("Offset: {}".format(offset))
            answer = read_Message(offset=offset)

            #print(json.dumps(answer, indent=2))

            for message in answer['result']:
                id = message['message']['from']['id']
                if 'text' in message['message']:
                    print("Text: " + str(message['message']['text']))
                    if message['message']['text'] == "/help":
                        send_Message(id, "/help - Zeige diese Hilfe an\n/batman - Ich Zeige dir, wer Batman ist!\n/batsignal - Rufe Batman""")
                    elif message['message']['text'] == "/batman":
                        send_Message(id, "Ich bin Batman!")
                        print("Batman")
                    elif message['message']['text'] == "/batsignal":
                        file = "https://upload.wikimedia.org/wikipedia/en/c/c6/Bat-signal_1989_film.jpg"
                        send_Photo(id, file)
                        print("Batsignal")
                    print(message)
                elif 'document' in message['message']:
                    print("Document: " + str(message['message']['document']))
                elif 'photo' in message['message']:
                    #print("Photo: " + str(message['message']['caption']))
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

                    send_Message(id, "Danke für das Bild. Ich habe es für die Verwendung in der Datenbank gespeichert.")
                    download_File(file, filename)
                    #print(filename)
                    print(type(message['update_id']))
                    return filename

                set_Last_Update_Id(message['update_id'] + 1, table)
                db_connection.commit()


            time.sleep(5)

    except KeyboardInterrupt:
        # Terminate the script and switch off all leds
        print("Press Ctrl-C to terminate while statement")
        #db_connection.commit()
        db_connection.close()


if __name__ == "__main__":
    main()