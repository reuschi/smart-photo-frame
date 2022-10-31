# Smart Photo Frame

## Introduction

This is a Smart Photo Frame to show a slideshow of pictures that were sent via email, via a Telegram Bot, or by dropping the files to an Owncloud share with the possibility to add more sources. Originally this was developed for my family, as we don't see each other so often and give a possibility to share images right from vacation or from far away. To run it completely, you need to create your own Telegram Bot token at *@BotFather*. Within your mailbox a folder named "Smart Photo Frame" should be present where all new photos for the frame will be automatically moved to. In your Owncloud share all images should be uploaded to a subfolder named "images". 

## Recommended hardware and software

**Computing Hardware:** Every RaspberryPi with wireless or wired connection (successfully running on ZeroW)\
**Display:** Each HDMI connectable display

**Operating System:** RaspberryPi OS (Lite installation is enough)\
**Python version:** 3.7+\
**Required Python Packages:** GitPython, requests, RPi.GPIO, urllib3, easywebdav2, Pillow\
**Required Linux Packages:** fbi, libopenjp2-7

## Installation guide

1. Install the package by cloning the repository
2. Create your own config.ini file (see chapter for config)
3. If you want to be able to update the frame via Telegram, you need to store your GitHub login data in store manager on RasPi and copy the ".gitconfig" and ".git-credentials" files to "/root".
4. Connect an HDMI screen to the RasPi (TV, computer monitor, HDMI display, etc.)

## Folder structure

When repository is cloned, no subfolders are created. To store your images, a subfolder named **"images"** will be created while importing the first image. Within this folder you can delete or add new photos manually or by Telegram command. After adding or deleting (if done by hand) the frame needs to be restarted manually. If uploaded or deleted by Telegram command, this is done automatically.\
All other data is stored in the main folder of the cloned repository.\
Automatic generated files by the frame are:
* telegram_bot.db
* messages.log

If you delete these files manually after creation, some errors may occur.

## Config file

The config file should be stored as **config.ini** in the same folder as the **main.py** and should look like the following:
```
[telegram]
token = <Your Telegram API Token>
allowedsenders = 123456789,<comma seperated Telegram user id's>
admins = <comma seperated Telegram user id's> ; will be allowed to send admin commands
auth_password = <admin password>
status_signal = True/False ; frame gives feedback via Telegram when it's started and shutdown
poll_timeout = 60 ; Timeout for long poll configuration
commands = [{"command": "deleteimg", "description": "Delete an image from frame"},
            {"command": "getconfig", "description": "Send configuration file as attachment"},
            {"command": "getident", "description": "Get current external ip address"},
            {"command": "getlog", "description": "Send log file as attachment"},
            {"command": "listimg", "description": "List all images stored on frame"},
            {"command": "reboot", "description": "Reboot whole system"},
            {"command": "rotate", "description": "Rotate image left or right"},
            {"command": "toggle_signaling", "description": "Switch the Telegram signaling"},
            {"command": "toggle_verbose", "description": "Toggle between showing or hiding image description"},
            {"command": "update", "description": "Update system with current master repository"}]

[mail]
account = <mail address>
password = <mail account password>
hostname = <hostname of imap or pop3 mail server>
fileExtensions = jpg,png,<comma seperated list of allowed file extensions - case-insensitive>

[owncloud]
host = <hostname>
username = <username>
password = <password>
delete_after_download = True/False ; remote files on owncloud will be deleted 
subfolder = <foldername> ; subfolder on owncloud

[frame]
timer = 10 ; single photo display time in seconds 
blend = 750 ; blend time between two photos in ms
photocount = 200 ; amount of maximum photos to circle
verbose = True/False ; verbose file information during slideshow

[logging]
logToFile = True/False ; set logging to file
logToScreen = True/False ; set logging to screen 

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

Now, the Bot should be ready to receive and send messages. If you send messages via web browser or mobile phone to the Bot while the frame is not running, nothing happens. To get a reply on your sent photos, you must run the **main.py**. In most cases the script must run as *sudo*.

## Current implemented Telegram Bot commands

As seen above in the config, the follwing bot commands will be placed to the bot configuration:

* */deleteimg <name_of_image_1>,<name_of_image_2>,etc.* - Deletes one or more images from images folder of the frame.
* */getconfig* - Returns the current config.ini as downloadable file.
* */getident* - Returns the current public IP address of the frame.
* */getlog* - Returns the message.log file from frame root as downloadable file.
* */listimg* - Lists all images stored in the images folder.
* */reboot* - Reboots the whole system (RasPi).
* */rotate <image_name_1>,<l/r> <image_name_2>,<l/r> etc.* - Rotates the named image(s) 90° to the left (l) or to the right (r). Files must be seperated by whitespaces and file names needs to be followed by orientation.
* */toggle_signaling* - Toggles the Feedback from the frame when it's booted up or shutting down.
* */toggle_verbose* - Toggled the display of additional information in the image presentation of the frame.
* */update (<repository_name>)* - Update system with current master repository. If entered a name, then this command tries to checkout and update the named branch.

You can add some more commands by your own by just adding them to the configuration. All of the listed commands will be pushed to the Telegram Bot when starting the frame.

## Preparing your mailbox

To only get those mails downloaded that are intended for the photo frame, you should create a subfolder in your mailbox. By default the system awaits the folder name to be **"Smart Photo Frame"**. You can change it in the source code as you want.\
New mails should be moved automatically to this subfolder or sorted out by an inbox rule.\
If you want to use a mailbox at Gmail, as I did, you need to adjust the mailbox settings. Either you activate the login for unsecure third party apps or you activate the 2FA and register another third party app where you create a new password which you can enter in the configuration of the Picture Frame.

## Preparing your Owncloud account

For the possibility to let the frame download images from your owncloud account, a subfolder named **"images"** should be added to the root directory. All files added to this folder will be downloaded by the frame and automatically deleted from the owncloud account, unless you deactivate the deletion by the config file.

## Creating the automatic run of the script

To run the frame automatically via bootup you additionally need to add the a new service to systemd to call **main.py**. A detailed instruction can be found here: \
https://www.thedigitalpictureframe.com/ultimate-guide-systemd-autostart-scripts-raspberry-pi/. \
When running the script on bootup, the output can be seen via
```
journalctl -l -f -u your.service
```
or otherwise just download the logfile.

## Hardware enhancements

By adding hardware buttons to the RasPi you can offer your Frame users the possibility to handle the Frame. There are already preparations done for three buttons in sum. One button can be used to rise the display time of each photo in steps of 2 seconds. Another button can be used to lower the display time of each photo - down to 2 seconds. The third button can be used to properly shut down the whole RasPi (e.g. for moving from one place to another or at night).\
Those three buttons are mentioned to be installed on the following ports:
* Pin 27: Rise the timer
* Pin 19: Lower the timer
* Pin 9: Shut down the system

All ports are configured as Pull-Up ports and need to be connected to ground.\
For my use case I soldered them directly on the RasPi and gave the buttons that raise and lower the timer a higher hardware button.

## Open tasks

- [ ] Complete the replacement of all texts in english and german
- [x] Implement another interconnection between frame and sender (OwnCloud, Dropbox, etc.)
- [ ] ~~Find a different presenter application to also display videos~~
- [ ] Complete the full implementation of OwnCloud