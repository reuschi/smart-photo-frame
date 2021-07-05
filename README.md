# Smart Photo Frame

## Introduction

This is a Smart Photo Frame to show a slideshow of pictures that were sent via email or via a Telegram Bot. To run it completely, you need to create your own Bot token at @BotFather.

## Recommended hard and software

Hardware: Every RaspberryPi with Wireless connection (successfully tested on Zero W)
Display: Each HDMI connectable display

System: RaspberryPi OS (installation without Desktop is enough)
Python version: 3.7
Packages: GitPython, requests, RPi.GPIO, urllib3

## Installation guide

1. Install the package by cloning the repository
2. Create a new subfolder "images" (here will all images be loaded into)
3. Create your own config.ini file (se the following chapter)
4. If you want to be able to update the frame via Telegram, you need to store your GitHub login data in store manager on raspi and copy the ".gitconfig" and ".git-credentials" files to "/root".
5. Connect an HDMI screen to the RasPi (TV, computer monitor, HDMI display, etc.)

## Config file

The config file should look like the following:
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
fileExtensions = jpg,JPG,png,PNG,<comma seperated list of file extensions>

[gmx]
account = <mail address>
password = <mail account password>
hostname = <hostname of mail server>
fileExtensions = jpg,JPG,png,PNG,<comma seperated list of file extensions>

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

## Creating the automatic run of the script

To run the frame automatically via bootup you additionally need to add the call of "main.py" to the "/etc/rc.local" file.