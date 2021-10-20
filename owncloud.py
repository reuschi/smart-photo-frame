import easywebdav2


class Owncloud:

    def __init__(self):
        self.host = "oc.reuschi.de"
        self.username = "reuschi"
        self.password = "OOU_usr42"

    def connect(self):
        self.owncloud = easywebdav2.connect(self.host, username=self.username, password=self.password)
        self.owncloud.cd("/remote.php/webdav/smart-photo-frame")

    def create_dir(self, dirname):
        print(self.owncloud.mkdir("/remote.php/webdav/" + dirname))

    def list(self):
        print(self.owncloud.ls())

    def download_file(self):
        list = self.list()

        for file in list:
            print(file[File])
        # self.owncloud.download()