"""Providing text modules for the whole package"""

texts = {
    "DE": {
        "tg": {
            "return_400": "400 - Fehlerhafte Anfrage!",
            "return_401": "401 - Nicht authorisiert!",
            "return_403": "403 - Ausführung verboten!",
            "return_404": "404 - Anfrage nicht gefunden",
            "return_406": "406 - Anfrage nicht ordnungsgemäß",
            "return_420": "420 - The maximum allowed number of attempts to invoke the given method with the given input parameters has been exceeded.",
            "return_500": "500 - An internal server error occurred while a request was being processed.",
            "thanks_image_upload": "Danke für das Bild. Ich habe es für die Verwendung in der Datenbank gespeichert und die Präsentation neu gestartet.",
            "sender_not_allowed": "Sie sind nicht berechtigt! ID:",
            "extension_not_allowed": "Die Dateierweiterung ist nicht erlaubt!",
            "new_file_extension": "Neue Extension(s) aufgenommen: {}",
            "new_sender_id": "Neue(n) Absender zur Liste hinzugefügt: {}",
            "id_delete_success": "Das Bild {} wurde erfolgreich gelöscht",
            "no_reboot_possible": "Reboot konnte nicht ausgeführt werden.",
            "sys_upd_success": "System erfolgreich aktualisiert.",
            "sys_upd_no_need": "System ist bereits auf dem neuesten Stand",
            "sys_upd_failed": "Update fehlgeschlagen",
            "sw_signaling_false": "Telegram signaling deaktiviert",
            "sw_signaling_true": "Telegram signaling aktiviert",
            "sw_signaling": "Status signaling auf {} gesetzt",
            "snd_signal": "System hochgefahren",
            "rotate_image_success": "Das Bild {} wurde erfolgreich gedreht",
            "rotate_image_fail": "Das Bild wurde nicht gedreht: {}",
            "toggle_verbose": "Anzeige von Bilddetails auf {} gesetzt",
            "rotate_index_error": "Bitte geben Sie den Befehl in folgendem Format an: '/rotate <dateiname>,<rotationsrichtung>'",
            "no_command_found": "Ungültiges Kommando verwendet",

        },
        "imap": {
            "no_mailbox_found": "FEHLER: Keine Mailbox zum Öffnen gefunden",
            "mailbox_open_error": "FEHLER: Keine Mailbox zum Öffnen gefunden. {}"
        },
        "google": {
            "file_exists": "Datei '{}' existiert bereits",
            "download_successfully": "'{}' erfolgreich heruntergeladen!",
            "download_failed": "Download von '{}' fehlgeschlagen!",
            "mail_deleted": "Mail {} gelöscht"
        },
        "frame": {

        },
        "owncloud": {
            "dir_create": "Directory {} created.",
            "file_deleted": "File {} deleted from Owncloud.",
            "file_downloaded": "File {} downloaded successfully from Owncloud.",

        },
        "log": {

        }
    },
    "EN": {
        "tg": {
            "return_400": "400 - Bad Request!",
            "return_401": "401 - You're not authorized!",
            "return_403": "403 - Action is Forbidden!",
            "return_404": "404 - Request not found",
            "return_406": "406 - Request not acceptable",
            "return_420": "420 - The maximum allowed number of attempts to invoke the given method with the given input parameters has been exceeded.",
            "return_500": "500 - An internal server error occurred while a request was being processed.",
            "thanks_image_upload": "Thank you for the image. I've stored it in the database and restarted the presentation.",
            "sender_not_allowed": "You're not authorized! ID: {}",
            "extension_not_allowed": "The file extension is not allowed!",
            "new_file_extension": "New extension(s) added: {}",
            "new_sender_id": "New sender added to allowed sender list: {}",
            "id_delete_success": "The image {} was deleted successfully",
            "no_reboot_possible": "Reboot could not be executed.",
            "sys_upd_success": "System update done",
            "sys_upd_no_need": "System was up to date",
            "sys_upd_failed": "System update failed!",
            "sw_signaling_false": "Telegram signaling deactivated",
            "sw_signaling_true": "Telegram signaling activated",
            "sw_signaling": "Status signaling set to {}",
            "snd_signal": "System is booted up",
            "rotate_image_success": "The image {} has been rotated successfully",
            "rotate_image_fail": "The image has not been rotated: {}",
            "toggle_verbose": "Verbose of details set to {}",
            "rotate_index_error": "Please send command in following format: '/rotate <filename>,<rotation_direction>'",
            "no_command_found": "Command could not be found",

        },
        "imap": {
            "no_mailbox_found": "ERROR: No Mailbox to open",
            "mailbox_open_error": "ERROR: Unable to open mailbox"
        },
        "google": {
            "file_exists": "File '{}' already exists",
            "download_successfully": "'{}' successfully downloaded!",
            "download_failed": "Download of '{}' failed!",
            "mail_deleted": "Mail {} deleted"
        },
        "frame": {

        },
        "owncloud": {
            "dir_create": "Directory {} created.",
            "file_deleted": "File {} deleted from Owncloud.",
            "file_downloaded": "File {} downloaded successfully from Owncloud.",

        },
        "log": {

        }
    }

}
