from imaplib import IMAP4_SSL
import email
import email.header
import os.path
import time


EMAIL_ACCOUNT = "spfreuschglock@gmail.com"
EMAIL_PASS = "lxLtuywaOS1gklsw2N1P"


def downloadAttachment(M, directory):

    rv, data = M.search(None, 'ALL')
    if rv != 'OK':
        print("No messages found!")
        return

    #print(rv)
    #print("Number of results: {0}".format(len(data[0].decode().split())))

    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print("ERROR getting message", num)
            return

        msg = email.message_from_bytes(data[0][1])
        # downloading attachments
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
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
                    print("New file downloaded: {}".format(filePath))
                else:
                    print("No new file downloaded!")
        try:
            if rv == 'OK':
                M.store(num, '+X-GM-LABELS', '\\Trash')
                M.expunge()
        except:
            continue


def initImap(username, password, hostname="imap.gmail.com"):
    Mail = IMAP4_SSL(host=hostname, port=993)
    print(Mail.welcome)
    try:
        rv, data = Mail.login(username, password)
    except IMAP4_SSL.error:
        print("LOGIN FAILED!!!")

    print(rv, data)

    rv, mailboxes = Mail.list()
    if rv == 'OK':
        print("Mailboxes:")
        print(mailboxes)

    rv, data = Mail.select('"Smart Photo Frame"')
    if rv == 'OK':
        print("Processing mailbox...\n")
        print(data)

        downloadAttachment(Mail, 'images/')
        Mail.close()
    else:
        print("ERROR: Unable to open mailbox {}".format(rv))


while True:
    initImap(EMAIL_ACCOUNT, EMAIL_PASS)
    time.sleep(60)
