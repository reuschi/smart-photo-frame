import easywebdav2
from collections import namedtuple


class Owncloud:

    def __init__(self):
        self.host = "oc.reuschi.de"
        self.username = "reuschi"
        self.password = "OOU_usr42"

    def connect(self):
        self.owncloud = easywebdav2.connect(self.host, username=self.username, password=self.password)
        self.owncloud.cd("/remote.php/webdav/smart-photo-frame")

    def create_dir(self, dirname):
        if not self.owncloud.exists("/remote.php/webdav/" + dirname):
            self.owncloud.mkdir("/remote.php/webdav/" + dirname)

    def ls(self):
        return self.owncloud.ls()

    def download_file(self):
        listing = self.ls()

        for file in listing:
            for field in file._fields:
                if getattr(file, "contenttype") == "image/jpeg":
                    print(getattr(file, "name"))

                # print(field)
                # print(getattr(file, field))
