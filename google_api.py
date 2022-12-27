""" Module to reach GMail, as IMAP connection is blocked by security reasons """

from pathlib import Path
import base64
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import module_log
import static_variables as static
import texts


class Gmail:
    """ Google API class """

    SCOPES = ["https://mail.google.com/"]

    def __init__(self, label="Smart Photo Frame"):
        self.creds = None
        self.label = label
        self._authorize()

    def _authorize(self):
        if Path("token.json").exists():
            self.creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                self.flow = InstalledAppFlow.from_client_secrets_file("credentials.json",
                                                                      self.SCOPES)
                self.creds = self.flow.run_local_server(port=0)
            with open("token.json", "w", encoding="UTF-8") as token:
                token.write(self.creds.to_json())

    def get_labels(self):
        """ Retrieve all configured labels """

        with build("gmail", "v1", credentials=self.creds) as service:
            labels = service.users().labels().list(userId="me").execute()

        return labels['labels']

    def get_label_id_by_name(self, name="Smart Photo Frame"):
        """ Retrieve label ID by its configured name """

        labels = self.get_labels()

        for label in labels:
            if name in label['name']:
                return label['id']

        return None

    def get_message_ids(self):
        """ Retrieve messageId of all message in mailbox """

        with build("gmail", "v1", credentials=self.creds) as service:
            messages = service.users().messages().list(userId="me").execute()

        return messages

    def read_message(self, message_id):
        """ Read message with msg_id """

        with build("gmail", "v1", credentials=self.creds) as service:
            message = service.users().messages().get(userId="me", id=message_id).execute()

        return message

    def delete_message(self, message_id):
        """ Delete a message from mailbox """

        with build("gmail", "v1", credentials=self.creds) as service:
            result = service.users().messages().trash(userId="me", id=message_id).execute()

        return result

    def read_attachment(self, message_id: str, attachment_id: str, filename: str,
                        destination: str = "images"):
        """ Read an attachment of a message and write it to the local file system """

        store_dir = Path(__file__).parent.absolute()
        extension = filename.split(".")[1]
        filename_base = filename.split(".")[0]
        filename = "mail_" + time.strftime("%Y%m%d_") + filename_base + "." + extension.lower()
        path = Path(store_dir / destination / filename)

        with build("gmail", "v1", credentials=self.creds) as service:
            attachment = service.users().messages().attachments().get(
                userId="me", messageId=message_id, id=attachment_id).execute()
            data = attachment['data']
            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))

            if path.exists():
                module_log.log(f"Datei '{filename}' existiert bereits")

            else:
                with open(path, 'wb') as file:
                    if file.write(file_data) > 0:
                        return True

            return False

    def download_attachment(self, mails, label=None):
        """ Download attachments from all mails in mailbox """

        success = False

        try:
            for mail in mails['messages']:
                #print(mail['id'])
                message = self.read_message(mail['id'])
                message_id = message["id"]
                message_parts = message["payload"]["parts"]

                for part in message_parts:
                    #print(f"Part-ID: {part['partId']}")
                    #print(f"Mime-Type: {part['mimeType']}")
                    #print(f"Filename: {part['filename']}")

                    extension = part['filename'].split(".")

                    if 'image' in part['mimeType'] and extension[1].lower() in static.file_extensions:
                        #print(f"Attachment-ID: {part['body']['attachmentId']}")
                        if self.read_attachment(message_id, part['body']['attachmentId'],
                                                part['filename']):
                            module_log.log(f"{part['filename']} erfolgreich heruntergeladen!")
                            success = True
                        else:
                            module_log.log(f"Download von {part['filename']} fehlgeschlagen!")
                            success = False
                    else:
                        continue

                if success:
                    #module_log.log(self.delete_message(message_id))
                    module_log.log(f"Mail {mail['id']} löschen")
                    success = False

        except Exception as exc:
            module_log.log(f"Exception during file download from mail: {exc}")

        return success
