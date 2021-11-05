import easywebdav2
import module_log
import static_variables
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
        module_log.log(f"File {path} deleted from Owncloud.")

    def download_file(self):
        listing = self.ls()
        success = False
        module_log.log("Requesting new files from OwnCloud...")

        try:
            for file in listing:
                if getattr(file, "contenttype") == "image/jpeg":
                    module_log.log("New file found on Owncloud. Start downloading")
                    path = getattr(file, "name")
                    filename = str(self._get_filename(path))
                    self.owncloud.download(path, "/home/pi/python/smart-photo-frame/images/" + filename)
                    success = True
                    module_log.log(f"File {filename} downloaded successfully from Owncloud.")
                    if static_variables.oc_delete:
                        self.delete_file(path)
            if not success:
                module_log.log("No new files found on OwnCloud.")
            return success
        except easywebdav2.WebdavException as e:
            module_log.log("Error while downloading")
            module_log.log(e)