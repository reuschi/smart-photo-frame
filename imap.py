from imaplib import IMAP4_SSL
import email
import email.header
import os.path
import time
import module_log


EMAIL_ACCOUNT = "spfreuschglock@gmail.com"
EMAIL_PASS = "lxLtuywaOS1gklsw2N1P"




def downloadAttachment(M, directory):

    rv, data = M.search(None, 'ALL')
    if rv != 'OK':
        module_log.log("Request to Mailbox unsuccessfull!")
        return

    if not data[0]:
        module_log.log("No new mail found")
    else:
        for num in data[0].split():
            module_log.log("Trying to donwload mail attachment...")

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
                    filePath = os.path.join(directory, fileName)

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
    Mail = IMAP4_SSL(host=hostname, port=993)
    #print(Mail.welcome)
    try:
        rv, data = Mail.login(username, password)

        #print(rv, data)

        rv, mailboxes = Mail.list()
        if rv == 'OK':
            module_log.log("Mailboxes found: " + str(mailboxes))
            #module_log.log(mailboxes)
        else:
            return "ERROR: No Mailbox to open"

        rv, data = Mail.select('"Smart Photo Frame"')
        if rv == 'OK':
            module_log.log("Processing mailbox...")
            #module_log.log(data)

            downloadAttachment(Mail, 'images/')
            Mail.close()
        else:
            return "ERROR: Unable to open mailbox {}".format(rv)
    except IMAP4_SSL.error as e:
        module_log.log(e)


def main():
    initImap(EMAIL_ACCOUNT, EMAIL_PASS)
    #time.sleep(60)


if __name__ == "__main__":
    main()