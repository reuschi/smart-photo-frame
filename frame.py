
#from pyrogram import Client, filters
import os
import subprocess
import time


images = []
timer = 8

def getFiles():
    for file in os.listdir(directory):
        images[file] = os.fsdecode(file)

    return images


def exitSlideshow():
    os.system("sudo killall -15 fbi")


def runSlideshow():
    global timer
    bashCommand = "sudo fbi --noverbose -a -t {} -T 1 images/*.jpg".format(timer)
    #bashCommand = ['fbi', '--noverbose', '-a', '-t', '7', '--vt', '1' 'images/1266.jpg']
    process = subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2)


    #output, error = process.communicate()
    #print(output)

    #os.system(bashCommand)

    #bashCommand = "sudo fbi --noverbose -a -t 7 /home/pi/python/smart-photo-frame/images/*.jpg -T 1"
    #os.system(bashCommand)


#api_id = 2640738
#api_hash = "1a909a049af457fff5e5cffdd4524199"


#app = Client("my_account")
#app.run()

#@app.on_message(filters.private)
#async def hello(client, message):
#    await message.reply_text(f"Hello {message.from_user.mention}")



if __name__ == '__main__':

    exitSlideshow()
    runSlideshow()

    while True:
        print("Was möchten Sie tun?")
        print("------")
        print("1 - Slideshow starten")
        print("2 - Slideshow beenden")
        print("3 - Frequenz erhöhen (-2 Sekunden)")
        print("4 - Frequenz verringern (+2 Sekunden)")
        print("0 - Exit")

        func = input("Bitte wählen Sie: ")

        if func == "1":
            runSlideshow()
        elif func == "2":
            exitSlideshow()
        elif func == "3":
            exitSlideshow()
            if timer >= 4:
                timer -= 2
            else:
                print("Timer bereits bei: {}. Frequenzerhöhung nicht möglich!".format(timer))
            runSlideshow()
        elif func == "4":
            exitSlideshow()
            timer += 2
            runSlideshow()
        elif func == "0":
            exitSlideshow()
            break
        else:
            print("Keine Aktion durchführbar!")



    #for file in images:
#    bashCommand = "sudo fbi --noverbose -a -t 7 /home/pi/python/smart-photo-frame/images/*.jpg -T 1"
#    os.system(bashCommand)
    #    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, shell=True)
    #    output, error = process.communicate()
    #time.sleep(5)
    #exitSlideshow()
#    kill = os.system("pgrep fbi")
#    print("fbi process number: {}".format(kill))
#    os.system("sudo pkill fbi")

#    proc1 = subprocess.Popen(["sudo", "fbi", "--noverbose", "-a", "-t", "7", "./images/*.jpg", "-T", "1"])
#    print("Process with ID {} is running".format(proc1.pid))
#    time.sleep(20)
#    proc1.terminate()
#    print("Process terminated")


