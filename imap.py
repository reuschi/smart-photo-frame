from imaplib import IMAP4_SSL
from socket import gethostbyname,gaierror
import email
import email.header
import os.path
import module_log
import pathlib
import static_variables
import texts


class ImapMail:

    def __init__(self, account: str, passwd: str, hostname: str, ext: str = "jpg,JPG", subfolder: str = "Smart Photo Frame"):
        self.EMAIL_ACCOUNT = account
        self.EMAIL_PASS = passwd
        self.hostname = hostname
        self.allowedExtensions = ext
        self.subfolder = subfolder
        self.language = static_variables.language

    def download_attachment(self, mail, directory: str = "images"):
        # Download attachments from mails sent to the mail account
        success = False
        rv, data = mail.search(None, 'ALL')
        if rv != 'OK':
            module_log.log("Request to Mailbox was not successful!")
            return False

        if not data[0]:
            module_log.log("No new mail found")
        else:
            for num in data[0].split():
                module_log.log("Trying to download mail attachment...")

                # Try to fetch new mails
                rv, data = mail.fetch(num, '(RFC822)')
                if rv != 'OK':
                    module_log.log("ERROR getting message")
                    return False

                msg = email.message_from_bytes(data[0][1])

                # Downloading attachments
                for part in msg.walk():
                    # Only download attachments, if they are real attachments
                    if part.get_content_maintype() == 'multipart':
                        continue
                    else:
                        module_log.log("No attachment found!")

                    if part.get('Content-Disposition') is None:
                        continue

                    # Get filename and extension of the downloadable file
                    file_name = "mail_" + part.get_filename()
                    file_extension = os.path.splitext(file_name)[1].lower().replace('.','')

                    # Only download file if its extension is on config file
                    if bool(file_name) and (file_extension in self.allowedExtensions):
                        # Define path where to store the file locally
                        file_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / directory / file_name.lower())

                        if not os.path.isfile(file_path):
                            # If file is not yet downloaded
                            fp = open(file_path, 'wb')
                            fp.write(part.get_payload(decode=True))
                            fp.close()
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
                    if rv == 'OK':
                        if "gmail.com" in self.hostname:
                            mail.store(num, '+X-GM-LABELS', '\\Trash')
                            mail.expunge()
                        else:
                            mail.store(num, '+FLAGS', '\\Deleted')
                except Exception as e:
                    module_log.log(e)

        return success

    def init_imap(self):
        # Receive new mails
        success = False
        try:
            module_log.log("Trying to fetch new mails")
            # Initialize connection and login to mail account
            imap = IMAP4_SSL(host=self.hostname, port=993)
            rv, data = imap.login(self.EMAIL_ACCOUNT, self.EMAIL_PASS)

            module_log.log(data)

            # Receive Mailboxes
            rv, mailboxes = imap.list()
            if rv == 'OK':
                module_log.log("Mailboxes found: " + str(mailboxes))
            else:
                module_log.log("No Mailbox found")
                return texts.texts[self.language]['imap']['no_mailbox_found']

            # Select mailbox folder to download images from and download new images
            rv, data = imap.select(f'"{self.subfolder}"')
            if rv == 'OK':
                module_log.log("Processing mailbox...")

                success = self.download_attachment(imap)
            else:
                return texts.texts[self.language]['imap']['mailbox_open_error'].format(rv)

            # Close connection to mail server
            imap.close()
            imap.logout()

        except gaierror as e:
            module_log.log("DNS name not resolvable. Try again later.")
        except IMAP4_SSL.error as e:
            module_log.log(e)
        except Exception as e:
            module_log.log(e)

        return success

