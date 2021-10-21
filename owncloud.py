import easywebdav2

import module_log
import static_variables
import
from collections import namedtuple


class Owncloud:

    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.connect()

    def connect(self):
        self.owncloud = easywebdav2.connect(self.host, username=self.username, password=self.password)
        self.owncloud.cd("/remote.php/webdav/images")

    def create_dir(self, dirname):
        if not self.owncloud.exists("/remote.php/webdav/" + dirname):
            self.owncloud.mkdir("/remote.php/webdav/" + dirname)
            module_log.log(f"Directory {dirname} created.")

    def ls(self):
        return self.owncloud.ls()

    def _get_filename(self, path: str):
        filename = path.split("/")
        return str(filename[-1])

    def delete_file(self, path):
        self.owncloud.delete(path)
        module_log.log(f"File {path} deleted.")

    def download_file(self):
        listing = self.ls()

        try:
            for file in listing:
                if getattr(file, "contenttype") == "image/jpeg":
                    module_log.log("New files found. Start downloading")
                    path = getattr(file, "name")
                    filename = str(self._get_filename(path))
                    self.owncloud.download(path, "/home/pi/python/smart-photo-frame/images/" + filename)
                    module_log.log(f"File {filename} downloaded successfully.")
                    if static_variables.oc_delete:
                        self.delete_file(path)


                    # print(field)
                    # print(getattr(file, field))
        except easywebdav2.WebdavException as e:
            module_log.log("Error while downloading")
            module_log.log(e)