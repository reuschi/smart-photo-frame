# Smart Photo Frame

## Introduction

This is a Smart Photo Frame to show a slideshow of pictures that were sent via email or via a Telegram Bot. To run it completely, you need to create your own Bot token at *@BotFather*. Within your mailbox a folder named "Smart Photo Frame" should be present where all new photos for the frame will be automatically moved to.

## Recommended hard and software

Hardware: Every RaspberryPi with Wireless connection (successfully tested on Zero W)\
Display: Each HDMI connectable display

System: RaspberryPi OS (installation without Desktop is enough)\
Python version: 3.7\
Packages: GitPython, requests, RPi.GPIO, urllib3

## Installation guide

1. Install the package by cloning the repository
2. Create a new subfolder "images" (here will all images be loaded into)
3. Create your own config.ini file (se the following chapter)
4. If you want to be able to update the frame via Telegram, you need to store your GitHub login data in store manager on RasPi and copy the ".gitconfig" and ".git-credentials" files to "/root".
5. Connect an HDMI screen to the RasPi (TV, computer monitor, HDMI display, etc.)

## Config file

The config file should be stored as config.ini in the same folder as the frame.py and should look like the following:
```
[telegram]
token = <Telegram API Token>
allowedsenders = 123456789,<comma seperated Telegram user id's>
admins = <comma seperated Telegram user id's>
auth_password = <admin password>
commands = [{"command": "getident", "description": "Get current external ip address"},
            {"command": "listimg", "description": "List all images stored on frame"},
            {"command": "getlog", "description": "Send log file as attachment"},
            {"command": "getconfig", "description": "Send configuration file as attachment"},
            {"command": "reboot", "description": "Reboot whole system"},
            {"command": "update", "description": "Update system with current repository"}]

[gmail]
account = <mail address>
password = <mail account password>
fileExtensions = jpg,JPG,png,PNG,<comma seperated list of allowed file extensions>

[gmx]
account = <mail address>
password = <mail account password>
hostname = <hostname of mail server>
fileExtensions = jpg,JPG,png,PNG,<comma seperated list of allowed file extensions>

[frame]
timer = 10 ; single photo display time in seconds 
blend = 750 ; blend time between two photos in ms
photocount = 200 ; amount of maximum photos to circle

[logging]
logToFile = True
logToScreen = True

[global]
language = EN ; available: EN & DE - other languages need to be added to texts.py
```

## Creating a Telegram Bot

You need to create your own Telegram Bot. For that just follow the tasks:
1. Open Telegram on your smartphone or in your browser (https://web.telegram.org/)
2. Search for the global contact *@BotFather*
3. Send the message "/newbot" and configure your Bot (name, settings, etc.)
4. Create or view the API Token of that Bot
5. Copy the token and store it in the config file as shown above
6. Open the conversation with the Bot

Now the Bot should be ready to receive messages. If you send messages to the Bot while the frame is not running, nothing is happening. To get a reply on your send photos, you must run the **"main.py"**.

## Preparing your mailbox

To only get those mails downloaded that are intended for the photo frame, you should create a subfolder in your mailbox. By default the system awaits the folder name to be "Smart Photo Frame". You can change it in the source code as you want.\
New mails should be moved automatically to this subfolder or sorted out by an inbox rule.

## Creating the automatic run of the script

To run the frame automatically via bootup you additionally need to add the call of **"main.py"** to the "/etc/rc.local" file.

## Hardware enhancements

By adding hardware buttons to the RasPi you can offer your Frame users the possibility to handle the Frame. There are already preparations done for three buttons in sum. One button can be used to rise the display time of each photo in steps of 2 seconds. Another button can be used to lower the display time of each photo - down to 2 seconds. The third button can be used to properly shut down the whole RasPi (e.g. for moving from one place to another or at night).\
Those thre buttons are are mentioned to be installed on the following ports:
* Port 27: Rise the timer
* Port 19: Lower the timer
* Port 9: Shut down the system

All ports are configured as Pull-Up ports and need to be connected to ground.\
For my use case I soldered them directly on the RasPi and gave the buttons that raise and lower the timer a higher button.

## Open tasks

- [ ] Complete the replacement of all texts
- [ ] Implement another interconnection between frame and sender (OwnCloud, Dropbox, etc.)
- [ ] Find a different presenter application to also display videos