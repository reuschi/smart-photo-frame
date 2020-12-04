
#from pyrogram import Client, filters
import os
import subprocess
import time


images = []


def getFiles():
    for file in os.listdir(directory):
        images[file] = os.fsdecode(file)

    return images


def exitSlideshow():
    os.system("sudo killall -15 fbi")


def runSlideshow():
    exitSlideshow()
    bashCommand = "sudo fbi --noverbose -a -t 7 /home/pi/python/smart-photo-frame/images/*.jpg -T 1"
    os.system(bashCommand)





#api_id = 2640738
#api_hash = "1a909a049af457fff5e5cffdd4524199"


#app = Client("my_account")
#app.run()

#@app.on_message(filters.private)
#async def hello(client, message):
#    await message.reply_text(f"Hello {message.from_user.mention}")



if __name__ == '__main__':
    #images = getFiles()

    runSlideshow()
    #for file in images:
#    bashCommand = "sudo fbi --noverbose -a -t 7 /home/pi/python/smart-photo-frame/images/*.jpg -T 1"
#    os.system(bashCommand)
    #    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    #    output, error = process.communicate()
    time.sleep(25)
    exitSlideshow()
#    kill = os.system("pgrep fbi")
#    print("fbi process number: {}".format(kill))
#    os.system("sudo pkill fbi")

#    proc1 = subprocess.Popen(["sudo", "fbi", "--noverbose", "-a", "-t", "7", "./images/*.jpg", "-T", "1"])
#    print("Process with ID {} is running".format(proc1.pid))
#    time.sleep(20)
#    proc1.terminate()
#    print("Process terminated")


