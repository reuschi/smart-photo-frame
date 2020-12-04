
#from pyrogram import Client, filters
#import os
import subprocess
import time




#api_id = 2640738
#api_hash = "1a909a049af457fff5e5cffdd4524199"


#app = Client("my_account")
#app.run()

#@app.on_message(filters.private)
#async def hello(client, message):
#    await message.reply_text(f"Hello {message.from_user.mention}")



if __name__ == '__main__':
#    app.run()
    proc1 = subprocess.Popen("sudo fbi -a -t 5 ./images/*.jpg -T 1")
    print("Process with ID {} is running".format(proc1.pid))
    time.sleep(10)
    proc1.terminate()
    print("Process terminated")