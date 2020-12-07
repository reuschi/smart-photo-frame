from imaplib import IMAP4_SSL
import email
import email.header
import datetime
import os.path


EMAIL_ACCOUNT = "spfreuschglock@gmail.com"
EMAIL_PASS = "lxLtuywaOS1gklsw2N1P"



def process_mailbox(M):
    """
    Do something with emails messages in the folder.
    For the sake of this example, print some headers.
    """

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
            # this part comes from the snipped I don't understand yet...
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            fileName = part.get_filename()
            fileExtension = os.path.splitext(fileName)[1]
            if bool(fileName) and (fileExtension == ".jpg" or fileExtension == ".png"):
                filePath = os.path.join('images/', fileName)
                if not os.path.isfile(filePath):
                    fp = open(filePath, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()
                    print("New file downloaded: {}".format(filePath))
                else:
                    print("No new file downloaded!")
        try:
            M.store(num, '+X-GM-LABELS', '\\Trash')
            M.expunge()
        except:
            continue

        #decode = email.header.decode_header(msg['From'])[0]
        #subject = str(decode[0])
        #print("Message {}: {}".format(num, subject))
        #print('Raw Date:', msg['Date'])
        # Now convert to local date-time
        #date_tuple = email.utils.parsedate_tz(msg['Date'])
        #if date_tuple:
        #    local_date = datetime.datetime.fromtimestamp(
        #        email.utils.mktime_tz(date_tuple))
        #    print("Local Date:", \
        #        local_date.strftime("%a, %d %b %Y %H:%M:%S"))


def initImap(username, password, host):
    Mail = IMAP4_SSL(host=host, port=993)
    print(Mail.welcome)
    try:
        rv, data = Mail.login(username, password)
    except IMAP4_SSL.error:
        print("LOGIN FAILED!!!")

    print(rv, data)

    #Mail.select("Smart Photo Frame", True)
    rv, mailboxes = Mail.list()
    if rv == 'OK':
        print("Mailboxes:")
        print(mailboxes)

    rv, data = Mail.select('"Smart Photo Frame"')
    if rv == 'OK':
        print("Processing mailbox...\n")
        print(data)
        process_mailbox(Mail)
        Mail.close()
    else:
        print("ERROR: Unable to open mailbox {}".format(rv))

    #rv, data = Mail.search(None, 'X-GM-RAW "{search} label:Smart Photo Frame"'.format(search="Subscription"), 'ALL')
    #if rv != 'OK':
    #    print("No messages found!")



initImap(EMAIL_ACCOUNT, EMAIL_PASS, "imap.gmail.com")
