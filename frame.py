""" This module is to control the frame process itself """

import os
import subprocess
import time
import glob
from pathlib import Path

import module_log
import static_variables as static


class Frame:
    """ Main class for frame and slideshow control """

    def __init__(self, timer: int, blend: int, max_photo: int):
        self.images = []
        self.timer = timer
        self.blend = blend  # in milliseconds
        self.max_photocount = max_photo

    @staticmethod
    def _run_subprocess(bash_command: str):
        """ Run a subprocess including the bash_command """

        try:
            with subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as reply:
                _output, error = reply.communicate()

            if "Terminated" not in str(error):
                return True

            # module_log.log("Standard output: " + str(output))
            module_log.log("Error output: " + str(error))
            return False

        except subprocess.SubprocessError as exc:
            module_log.log(exc)
            return False

    def exit_slideshow(self):
        """ Kill all running processes of the slideshow """

        bash_command = "sudo killall -15 fbi"
        if self._run_subprocess(bash_command):
            module_log.log("Slideshow killed")

    def delete_old_files(self, directory: str = "images", maximum: int = None):
        """ Delete older image files in 'directory' that are over amount 'max' """

        if maximum is None:
            maximum = self.max_photocount

        module_log.log("Checking for old files to be deleted...")
        file_path = Path(Path(__file__).parent.absolute() / directory / "*.*")
        delete = False

        files = glob.glob(str(file_path))
        files.sort(key=os.path.getmtime, reverse=True)

        for index in range(maximum, len(files)):
            bash_command = f"sudo rm {files[index]}"
            if not self._run_subprocess(bash_command):
                module_log.log(f"Removing the file {files[index]} was NOT successful.")

            delete = True

        if delete:
            module_log.log("Deleting old files is done.")
        else:
            module_log.log("There were no files to be deleted.")

    def run_slideshow(self, path: str = "images", verbose: bool = False):
        """ Start the slideshow with all present files in subfolder defined in variable 'path' """

        path = Path(Path(__file__).parent.absolute() / path / "*.*")
        if verbose:
            bash_command = f"sudo fbi --random --blend {self.blend} -a -t {self.timer} -T 1 {path}"
        else:
            bash_command = f"sudo fbi --noverbose --random --blend {self.blend}" \
                           f" -a -t {self.timer} -T 1 {path}"

        slideshow = self._run_subprocess(bash_command)
        # Needed implementation for RaspiZeroW to not terminate the start of the
        # framebuffer while booting up
        #time.sleep(2)
        module_log.log("Slideshow running")
        return slideshow

    def restart_slideshow(self, verbose: bool = False):
        """ Stop slideshow and restart the slideshow with the new added image files """

        module_log.flush_log_file()
        module_log.log("Slideshow restarting")
        self.exit_slideshow()
        self.delete_old_files()
        if not self.run_slideshow(verbose=verbose):
            self.run_slideshow(verbose=verbose)

    def rise_timer(self, _channel):
        """ Rise timer of presentation, to lower the showing frequency """

        self.timer += 2
        static.change_config_value('frame', 'timer', str(self.timer))
        module_log.log(f"Timer raised to: {self.timer}.")
        self.restart_slideshow()

    def lower_timer(self, _channel):
        """ Lower timer of presentation, to rise the showing frequency """

        if self.timer >= 4:
            self.timer -= 2
            static.change_config_value('frame', 'timer', str(self.timer))
            module_log.log(f"Timer lowered to: {self.timer}.")
            self.restart_slideshow()
        else:
            module_log.log(f"Timer already at: {self.timer}. Lowering not possible!")

    def system_shutdown(self, _channel):
        """ Shutdown the whole system """

        #module_log.log("!!!! SYSTEM IS GOING TO SHUTDOWN !!!!")
        bash_command = "sudo poweroff"
        if self._run_subprocess(bash_command):
            module_log.log("!!!! SYSTEM IS GOING TO SHUTDOWN !!!!")
        time.sleep(1)
