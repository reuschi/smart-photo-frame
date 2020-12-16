from imaplib import IMAP4_SSL
from socket import gethostbyname,gaierror
import email
import email.header
import os.path
import time
import module_log
import pathlib
import static_variables


# EMAIL_ACCOUNT = "spfreuschglock@gmail.com"
# EMAIL_PASS = "lxLtuywaOS1gklsw2N1P"

config = configparser.ConfigParser()
config.read('config.ini')

EMAIL_ACCOUNT = static_variables.EMAIL_ACCOUNT
EMAIL_PASS = static_variables.EMAIL_PASS



def downloadAttachment(M, directory='images'):

    rv, data = M.search(None, 'ALL')
    if rv != 'OK':
        module_log.log("Request to Mailbox was not successfull!")
        return

    if not data[0]:
        module_log.log("No new mail found")
    else:
        for num in data[0].split():
            module_log.log("Trying to download mail attachment...")

            rv, data = M.fetch(num, '(RFC822)')
            if rv != 'OK':
                module_log.log("ERROR getting message", num)
                return

            msg = email.message_from_bytes(data[0][1])

            # downloading attachments
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                else:
                    module_log.log("No attachment found!")

                if part.get('Content-Disposition') is None:
                    continue

                # get filename and extension of the downloadable file
                fileName = "mail_" + part.get_filename()
                fileExtension = os.path.splitext(fileName)[1]

                # only download file if its extension is .jpg or .png
                if bool(fileName) and (fileExtension == ".jpg" or fileExtension == ".png"):
                    # define path where to store the file
                    #filePath = os.path.join(directory, fileName)
                    filePath = pathlib.Path(pathlib.Path(__file__).parent.absolute() / directory / fileName)

                    # if file is not yet downloaded
                    if not os.path.isfile(filePath):
                        fp = open(filePath, 'wb')
                        fp.write(part.get_payload(decode=True))
                        fp.close()
                        module_log.log("New file downloaded: {}".format(filePath))
                    else:
                        module_log.log("No new file downloaded!")
            #if msg == False:
            #    logging.log("No new mails arrived.")
            try:
                if rv == 'OK':
                    M.store(num, '+X-GM-LABELS', '\\Trash')
                    M.expunge()
            except Exception as e:
                module_log.log(e)
                #continue


def initImap(username, password, hostname="imap.gmail.com"):
    try:
        module_log.log("Trying to fetch new mails")
        Mail = IMAP4_SSL(host=hostname, port=993)
        rv, data = Mail.login(username, password)

        module_log.log(data)

        rv, mailboxes = Mail.list()
        if rv == 'OK':
            module_log.log("Mailboxes found: " + str(mailboxes))
            #module_log.log(mailboxes)
        else:
            module_log.log("No Mailbox found")
            return "ERROR: No Mailbox to open"

        rv, data = Mail.select('"Smart Photo Frame"')
        if rv == 'OK':
            module_log.log("Processing mailbox...")

            downloadAttachment(Mail)
        else:
            return "ERROR: Unable to open mailbox {}".format(rv)

        Mail.close()
        Mail.logout()
    except gaierror as e:
        module_log.log("DNS name not resolveable. Try again later.")
    except IMAP4_SSL.error as e:
        module_log.log(e)
    except Exception as e:
        module_log.log(e)


def main():
    initImap(EMAIL_ACCOUNT, EMAIL_PASS)
    #time.sleep(60)


if __name__ == "__main__":
    main()