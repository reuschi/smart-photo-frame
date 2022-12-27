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
        if Path(Path(__file__).parent.absolute() / "token.json").exists():
            self.creds = Credentials.from_authorized_user_file(
                str(Path(Path(__file__).parent.absolute() / "token.json")), self.SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                file_path = str(Path(Path(__file__).parent.absolute() / "credentials.json"))
                print(file_path)
                self.flow = InstalledAppFlow.from_client_secrets_file(file_path, self.SCOPES)
                self.creds = self.flow.run_local_server(port=0)
            with open(str(Path(Path(__file__).parent.absolute() / "token.json")), "w", encoding="UTF-8") as token:
                token.write(self.creds.to_json())

    def _reformat_filename(self, filename):
        """ Reformat filename for correct download storage """

        filename = filename.replace("ß", "ss")
        filename = filename.replace("ä", "ae")
        filename = filename.replace("ö", "oe")
        filename = filename.replace("ü", "ue")
        filename = filename.replace(" ", "_")
        filename = filename.replace("/", "_")

        name = filename.split(".")[0]
        extension = filename.split(".")[1]

        new_filename = "mail_" + time.strftime("%Y%m%d_") + name + "." + extension.lower()

        return new_filename

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

    def get_message_ids_by_label_name(self, label="Smart Photo Frame"):
        """ Retrieve only messages with defined label set """

        mails = self.get_message_ids()
        label_id = self.get_label_id_by_name(label)

        new_mails = {}

        for message in mails['messages']:
            if label_id in message['labelIds']:
                #new_mails['messages'].
                pass

        return new_mails

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
        #extension = filename.split(".")[1]
        #filename_base = filename.split(".")[0]
        #filename = "mail_" + time.strftime("%Y%m%d_") + filename_base + "." + extension.lower()
        path = Path(store_dir / destination / self._reformat_filename(filename))

        with build("gmail", "v1", credentials=self.creds) as service:
            attachment = service.users().messages().attachments().get(
                userId="me", messageId=message_id, id=attachment_id).execute()
            data = attachment['data']
            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))

            if path.exists():
                module_log.log(texts.texts[static.language]['google']['file_exists'].format(filename))

            else:
                with open(path, 'wb') as file:
                    if file.write(file_data) > 0:
                        return True

            return False

    def download_attachment(self, mails, label=None):
        """ Download attachments from all mails in mailbox """

        success = False
        restart = False

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
                            module_log.log(texts.texts[static.language]['google']['download_successfully'].
                                           format(part['filename']))
                            success = True
                            restart = True
                        else:
                            module_log.log(texts.texts[static.language]['google']['download_failed'].
                                           format(part['filename']))
                            success = False
                    else:
                        continue

                if success:
                    #module_log.log(self.delete_message(message_id))
                    module_log.log(texts.texts[static.language]['google']['mail_deleted'].format(mail['id']))
                    success = False

        except Exception as exc:
            module_log.log(f"Exception during file download from mail: {exc}")

        return restart
