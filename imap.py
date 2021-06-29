from imaplib import IMAP4_SSL
from socket import gethostbyname,gaierror
import email
import email.header
import os.path
import module_log
import pathlib


class ImapMail:

    def __init__(self, account, passwd, hostname="imap.gmail.com", ext="jpg,JPG"):
        self.EMAIL_ACCOUNT = account
        self.EMAIL_PASS = passwd
        self.hostname = hostname
        self.allowedExtensions = ext

    def download_attachment(self, M, directory="images"):
        # Download attachments from mails sent to the mail account
        success = False
        rv, data = M.search(None, 'ALL')
        if rv != 'OK':
            module_log.log("Request to Mailbox was not successful!")
            return False

        if not data[0]:
            module_log.log("No new mail found")
        else:
            for num in data[0].split():
                module_log.log("Trying to download mail attachment...")

                # Try to fetch new mails
                rv, data = M.fetch(num, '(RFC822)')
                if rv != 'OK':
                    module_log.log("ERROR getting message", num)
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
                        file_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / directory / file_name)

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
                            M.store(num, '+X-GM-LABELS', '\\Trash')
                            M.expunge()
                        else:
                            M.store(num, '+FLAGS', '\\Deleted')
                except Exception as e:
                    module_log.log(e)

        return success

    def init_imap(self, username, password, hostname="imap.gmail.com"):
        # Receive new mails
        success = False
        try:
            module_log.log("Trying to fetch new mails")
            # Initialize connection and login to mail account
            Mail = IMAP4_SSL(host=self.hostname, port=993)
            rv, data = Mail.login(self.EMAIL_ACCOUNT, self.EMAIL_PASS)

            module_log.log(data)

            # Receive Mailboxes
            rv, mailboxes = Mail.list()
            if rv == 'OK':
                module_log.log("Mailboxes found: " + str(mailboxes))
            else:
                module_log.log("No Mailbox found")
                return "ERROR: No Mailbox to open"

            # Select mailbox folder to download images from and download new images
            rv, data = Mail.select('"Smart Photo Frame"')
            if rv == 'OK':
                module_log.log("Processing mailbox...")

                success = self.download_attachment(Mail)
            else:
                return f"ERROR: Unable to open mailbox {rv}"

            # Close connection to mail server
            Mail.close()
            Mail.logout()

        except gaierror as e:
            module_log.log("DNS name not resolvable. Try again later.")
        except IMAP4_SSL.error as e:
            module_log.log(e)
        except Exception as e:
            module_log.log(e)

        return success


def main():
    mail = ImapMail()
    return mail.init_imap(mail.EMAIL_ACCOUNT, mail.EMAIL_PASS)


if __name__ == "__main__":
    main()