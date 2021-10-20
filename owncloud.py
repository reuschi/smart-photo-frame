import easywebdav2


class Owncloud:

    def __init__(self):
        self.host = "oc.reuschi.de"
        self.username = "reuschi"
        self.password = "OUO_usr42"

    def connect(self):
        self.owncloud = easywebdav2.connect(self.host, username=self.username, password=self.password)

    def create_dir(self, dirname):
        self.owncloud.mkdir(dirname)