""" Module to control Owncloud connection """

from pathlib import Path
import easywebdav2

import module_log
import static_variables as static


class Owncloud:
    """ Owncloud connection """

    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.owncloud = None
        self.connect()

    def connect(self):
        """ Connect to the webdav webservice of owncloud """

        self.owncloud = easywebdav2.connect(self.host, username=self.username,
                                            password=self.password)
        self.owncloud.cd("/remote.php/webdav/" + static.oc_subfolder)

    def create_dir(self, dirname: str):
        """ Create a sub directory """

        if not self.owncloud.exists("/remote.php/webdav/" + dirname):
            self.owncloud.mkdir("/remote.php/webdav/" + dirname)
            module_log.log(f"Directory {dirname} created.")

    def list(self):
        """ List folders and files """

        try:
            return self.owncloud.ls()
        except ConnectionError:
            module_log.log("Connection Error. Connection reset by peer. Try again.")

        return None

    @staticmethod
    def _get_filename(path: str):
        """ Get filename of all files in sub directory """

        filename = path.split("/")
        return str(filename[-1])

    def delete_file(self, path: str):
        """ Delete a file from owncloud """

        self.owncloud.delete(path)
        module_log.log(f"File {path} deleted from Owncloud.")

    def download_file(self):
        """ Download a file """

        listing = self.list()
        success = False
        module_log.log("Requesting new files from OwnCloud...")

        try:
            for file in listing:
                if getattr(file, "contenttype") == "image/jpeg":
                    module_log.log("New file found on Owncloud. Start downloading.")
                    path = getattr(file, "name")
                    filename = str(self._get_filename(path))
                    upload_path = Path(Path(__file__).parent.absolute() / "images" / filename)
                    self.owncloud.download(path, upload_path)
                    success = True
                    module_log.log(f"File {filename} downloaded successfully from Owncloud.")
                    if static.oc_delete:
                        self.delete_file(path)
            if not success:
                module_log.log("No new files found on OwnCloud.")
            return success
        except easywebdav2.WebdavException as exc:
            module_log.log("Error while downloading.")
            module_log.log(exc)
            return False
