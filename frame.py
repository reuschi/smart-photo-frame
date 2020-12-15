
#from pyrogram import Client, filters
import os
import subprocess
import time
import imap
import telegram
import module_log
import glob
import pathlib


images = []
timer = 8
blend = 1000    # in milliseconds


def get_Files():
    for file in os.listdir(directory):
        images[file] = os.fsdecode(file)

    return images


def exit_Slideshow():
    try:
        os.system("sudo killall -15 fbi")
        module_log.log("Slideshow killed")
    except Exception as e:
        module_log.log(e)


def delete_Old_Files(directory="images", max=50):
    file_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / directory / "*.*")
    module_log.log("Files should be deleted")

    files = glob.glob(str(file_path))
    files.sort(key=os.path.getmtime, reverse=True)

    for x in range(max, len(files)):
        #print(files[x], os.path.getmtime(files[x]))
        try:
            os.remove(files[x])
        except Exception as e:
            module_log.log("Removing the file {} was NOT successful: {}".format(files[x], e))

    module_log.log("Deleting old files is done.")

    #for file in files:
    #print(files[10])
    #print(files)


def run_Slideshow(path='images'):

    path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / path / "*.*")
    bashCommand = "sudo fbi --noverbose --random --blend {} -a -t {} -T 1 {}".format(blend, timer, path)
    #bashCommand = ['fbi', '--noverbose', '-a', '-t', '7', '--vt', '1' 'images/1266.jpg']
    process = subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.5)

    module_log.log("Slideshow running")


    #output, error = process.communicate()
    #print(output)

    #os.system(bashCommand)

    #bashCommand = "sudo fbi --noverbose -a -t 7 /home/pi/python/smart-photo-frame/images/*.jpg -T 1"
    #os.system(bashCommand)


def restart_Slideshow():
    exit_Slideshow()
    delete_Old_Files()
    run_Slideshow()


if __name__ == '__main__':

    restart_Slideshow()

    i = 0
    time.sleep(15)

    while True:
        #print("Was möchten Sie tun?")
        #print("------")
        #print("1 - Slideshow starten")
        #print("2 - Slideshow beenden")
        #print("3 - Frequenz erhöhen (-2 Sekunden)")
        #print("4 - Frequenz verringern (+2 Sekunden)")
        #print("0 - Exit")

        #func = input("Bitte wählen Sie: ")

        #if func == "1":
        #    run_Slideshow()
        #elif func == "2":
        #    exit_Slideshow()
        #elif func == "3":
        #    if timer >= 4:
        #        timer -= 2
        #    else:
        #        print(f"Timer bereits bei: {timer}. Frequenzerhöhung nicht möglich!")
        #    restart_Slideshow()
        #elif func == "4":
        #    timer += 2
        #    restart_Slideshow()
        #elif func == "0":
        #    exit_Slideshow()
        #    break
        #else:
        #    print("Keine Aktion durchführbar!")

        #print("i: " + str(i))

        if i >= 4:
            imap.main()
            i = 0
        else:
            i += 1


        tg = telegram.main()
        if tg == True:
            module_log.log("Slideshow restart")
            restart_Slideshow()

        time.sleep(15)



