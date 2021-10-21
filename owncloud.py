import easywebdav2
import static_variables
from collections import namedtuple


class Owncloud:

    def __init__(self):
        self.host = static_variables.oc_host
        self.username = static_variables.oc_username
        self.password = static_variables.oc_password

    def connect(self):
        self.owncloud = easywebdav2.connect(self.host, username=self.username, password=self.password)
        self.owncloud.cd("/remote.php/webdav/smart-photo-frame")

    def create_dir(self, dirname):
        if not self.owncloud.exists("/remote.php/webdav/" + dirname):
            self.owncloud.mkdir("/remote.php/webdav/" + dirname)

    def ls(self):
        return self.owncloud.ls()

    def _get_filename(self, path: str):
        filename = path.split("/")
        return str(filename[-1])

    def download_file(self):
        listing = self.ls()

        for file in listing:
            if getattr(file, "contenttype") == "image/jpeg":
                path = getattr(file, "name")
                print(self.owncloud.download(path, "/home/pi/python/smart-photo-frame/images/" + self._get_filename(path)))

                # print(field)
                # print(getattr(file, field))
