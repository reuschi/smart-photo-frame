""" Fetching new mails from specific mail account """

from imaplib import IMAP4_SSL
from socket import gaierror
import email
import email.header
import os.path
import pathlib

import module_log
import static_variables
import texts


class ImapMail:
    """ Get mails and process the attachments """

    def __init__(self, account: str, passwd: str, hostname: str,
                 ext: str = "jpg,JPG", subfolder: str = "Smart Photo Frame"):
        self.email_account = account
        self.email_password = passwd
        self.hostname = hostname
        self.allowed_extensions = ext
        self.subfolder = subfolder
        self.language = static_variables.language

    def download_attachment(self, mail, directory: str = "images"):
        """
        Download attachments from mails stored in a specific sub folder

        :param mail:
        :param directory:
        :return:
        """

        success = False
        receive, data = mail.search(None, 'ALL')
        if receive != 'OK':
            module_log.log("Request to Mailbox was not successful!")
            return False

        if not data[0]:
            module_log.log("No new mail found")
        else:
            for num in data[0].split():
                module_log.log("Trying to download mail attachment...")

                # Try to fetch new mails
                receive, data = mail.fetch(num, '(RFC822)')
                if receive != 'OK':
                    module_log.log("ERROR getting message")
                    return False

                msg = email.message_from_bytes(data[0][1])

                # Downloading attachments
                for part in msg.walk():
                    # Only download attachments, if they are real attachments
                    if part.get_content_maintype() == 'multipart':
                        continue

                    module_log.log("No attachment found!")

                    if part.get('Content-Disposition') is None:
                        continue

                    # Get filename and extension of the downloadable file
                    file_name = "mail_" + part.get_filename()
                    file_extension = os.path.splitext(file_name)[1].lower().replace('.','')

                    # Only download file if its extension is in config file
                    if bool(file_name) and (file_extension in self.allowed_extensions):
                        # Define path where to store the file locally
                        file_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() /
                                                 directory / file_name.lower())

                        if not os.path.isfile(file_path):
                            # If file is not yet downloaded
                            file = open(file_path, 'wb')
                            file.write(part.get_payload(decode=True))
                            file.close()
                            module_log.log(f"New file downloaded: {file_path}")
                            success = True
                        elif os.path.isfile(file_path):
                            # If file already exists, don't download it
                            module_log.log("Filename already exists!")
                        else:
                            # If there is no new file to download
                            module_log.log("No new file downloaded!")
                    else:
                        # If file extension is not allowed to download
                        module_log.log(f"File Extension not allowed ('{file_extension}')")

                # After downloading the attachments move the mail into Trash folder
                try:
                    if receive == 'OK':
                        if "gmail.com" in self.hostname:
                            mail.store(num, '+X-GM-LABELS', '\\Trash')
                            mail.expunge()
                        else:
                            mail.store(num, '+FLAGS', '\\Deleted')
                except Exception as exc:
                    module_log.log(exc)

        return success

    def init_imap(self):
        """
        Receive new mails

        :return:
        """

        success = False
        try:
            module_log.log("Trying to fetch new mails")
            # Initialize connection and login to mail account
            imap = IMAP4_SSL(host=self.hostname, port=993)
            receive, data = imap.login(self.email_account, self.email_password)

            module_log.log(data)

            # Receive Mailboxes
            receive, mailboxes = imap.list()
            if receive == 'OK':
                module_log.log("Mailboxes found: " + str(mailboxes))
            else:
                module_log.log("No Mailbox found")
                return texts.texts[self.language]['imap']['no_mailbox_found']

            # Select mailbox folder to download images from and download new images
            receive, data = imap.select(f'"{self.subfolder}"')
            if receive == 'OK':
                module_log.log("Processing mailbox...")

                success = self.download_attachment(imap)
            else:
                return texts.texts[self.language]['imap']['mailbox_open_error'].format(receive)

            # Close connection to mail server
            imap.close()
            imap.logout()

        except gaierror:
            module_log.log("DNS name not resolvable. Try again later.")
        except IMAP4_SSL.error as exc:
            module_log.log(exc)
        except Exception as exc:
            module_log.log(exc)

        return success
