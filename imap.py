""" Fetching new mails from specific mail account """

from imaplib import IMAP4_SSL
from socket import gaierror
import email
import email.header
import time
from pathlib import Path

import module_log
import static_variables as static
import texts


class ImapMail:
    """ Get mails and process the attachments """

    def __init__(self, account: str, passwd: str, hostname: str,
                 ext: str = "jpg,JPG", subfolder: str = "Smart Photo Frame"):
        self.email_account = account
        self.email_password = passwd
        self.hostname = hostname
        self.allowed_extensions = static.file_extensions
        self.subfolder = subfolder
        self.language = static.language
        self.allowed_senders = static.mail_allowed_senders
        self.imap = None

    def fetch_messages(self):
        """ Build search string and search for messages only from allowed senders """

        search_string = ""

        if len(self.allowed_senders) > 1:
            search_string = "OR "

        for sender in self.allowed_senders:
            search_string += f"FROM {sender} "

        search_string = search_string.strip()
        if static.debug:
            module_log.log(f"Mail Sender Search-String: {search_string}")

        #receive, data = self.imap.search(None, 'ALL')
        receive, data = self.imap.search(None, search_string)
        if receive != 'OK':
            module_log.log("Request to Mailbox was not successful!")
            return None

        return data

    def get_filename(self, part):
        """ Get filename and extension of the downloadable file """

        if part.get_filename():
            #cur_time = str(int(time.time())) + "_"
            cur_time = time.strftime("%Y%m%d_%H%M%S") + "_"
            file_name = "mail_" + cur_time + part.get_filename()
            file_extension = Path(file_name).suffix.replace('.', '').lower()
            module_log.log(f"File Extension: {file_extension}")

            file = {
                'name': file_name,
                'extension': file_extension
            }
        else:
            file = None

        return file

    def get_attachment(self, part, directory, success):
        """ Get attachment of mail and write it into the correct directory """

        # Get filename and extension of the downloadable file
        file = self.get_filename(part)

        # Only download file if its extension is in config file
        if file and (file['extension'] in self.allowed_extensions):
            # Define path where to store the file locally
            file_path = Path(Path(__file__).parent.absolute() / directory /
                             file['name'].lower())

            if not Path.is_file(file_path):
                # If file is not yet downloaded
                with open(file_path, 'wb') as file:
                    file.write(part.get_payload(decode=True))
                module_log.log(f"New file downloaded: {file_path}")
                success = True
            elif Path.is_file(file_path):
                # If file already exists, don't download it
                module_log.log("Filename already exists!")
            else:
                # If there is no new file to download
                module_log.log("No new file downloaded!")
        else:
            # If file extension is not allowed to download
            module_log.log(f"File Extension not allowed ('{file['extension']}')")

        return success

    def delete_message(self, num):
        """ Delete mail from inbox / subfolder """

        try:
            if "gmail.com" in self.hostname:
                self.imap.store(num, '+X-GM-LABELS', '\\Trash')
            else:
                self.imap.store(num, '+FLAGS', '\\Deleted')
        except Exception as exc:
            module_log.log(f"Exception while delete: {exc}")

    def download_attachment(self, directory: str = "images"):
        """ Download attachments from mails stored in a specific sub folder """

        success = False

        data = self.fetch_messages()

        # Check if there is a new mail
        if not data[0]:
            module_log.log("No new mail found")
            return False

        # Run through new mails
        for num in data[0].split():
            module_log.log("Trying to fetch new mail...")

            # Try to fetch new mails
            receive, data = self.imap.fetch(num, '(RFC822)')

            if receive != 'OK':
                module_log.log("ERROR getting message")
                return False

            msg = email.message_from_bytes(data[0][1])

            # Downloading attachments
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart' or \
                        part.get('Content-Disposition') is None:
                    module_log.log("No attachment found!")
                    continue

                if static.debug:
                    module_log.log(f"Content-Type: {part.get_content_type()}")

                # Only download attachments, if they are real attachments
                if "image" in part.get_content_type():
                    module_log.log("Image in attachment found")
                    success = self.get_attachment(part, directory, success)

            # After downloading the attachments move the mail into Trash folder
            if receive == 'OK':
                self.delete_message(num)

                if static.debug:
                    module_log.log(f"{num} deleted")

        return success

    def imap_login(self):
        """ Login to imap account """

        self.imap = IMAP4_SSL(host=self.hostname, port=993)
        _receive, data = self.imap.login(self.email_account, self.email_password)

        # For debugging purposes
        if static.debug:
            module_log.log(data)

    def imap_close_connection(self):
        """ Empty trash and close connection to mail server """

        self.imap.expunge()
        self.imap.close()
        self.imap.logout()

    def init_imap(self):
        """ Receive new mails """

        success = False

        try:
            module_log.log("Trying to fetch new mails")
            # Initialize connection and login to mail account
            self.imap_login()

            # Receive Mailboxes
            receive, mailboxes = self.imap.list()
            if receive == 'OK':
                module_log.log("Mailbox found")

                if static.debug:
                    # For debugging purposes
                    module_log.log(str(mailboxes))
            else:
                module_log.log("No Mailbox found")
                return texts.texts[self.language]['imap']['no_mailbox_found']

            # Select mailbox folder to download images from and download new images
            receive, _data = self.imap.select(f'"{self.subfolder}"')
            if receive == 'OK':
                module_log.log("Processing mailbox...")

                success = self.download_attachment()
            else:
                return texts.texts[self.language]['imap']['mailbox_open_error'].format(receive)

            # Close connection to mail server
            self.imap_close_connection()

        except gaierror:
            module_log.log("DNS name not resolvable. Try again later.")
        except IMAP4_SSL.error as exc:
            module_log.log(exc)
        except Exception as exc:
            module_log.log(exc)

        return success
