import os
import subprocess
import time
import module_log
import glob
import pathlib


class Frame:

    def __init__(self, timer, blend, max_photo):
        self.images = []
        self.timer = timer
        self.blend = blend  # in milliseconds
        self.max_photocount = max_photo

    def exit_slideshow(self):
        # Kill all running processes of the slideshow
        try:
            #os.system("sudo killall -15 fbi")
            bash_command = f"sudo killall -15 fbi"
            subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            module_log.log("Slideshow killed")
        except Exception as e:
            module_log.log(e)

    def delete_old_files(self, directory: str = "images", maximum: int = None):
        # Delete older image files in 'directory' that are over amount 'max'
        if maximum is None:
            maximum = self.max_photocount

        module_log.log("Checking for old files to be deleted...")
        file_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / directory / "*.*")
        delete = False

        files = glob.glob(str(file_path))
        files.sort(key=os.path.getmtime, reverse=True)

        for x in range(maximum, len(files)):
            try:
                bash_command = f"sudo rm {files[x]}"
                subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                delete = True
            except Exception as e:
                module_log.log(f"Removing the file {files[x]} was NOT successful: {e}")

        if delete:
            module_log.log("Deleting old files is done.")
        else:
            module_log.log("There were no files to be deleted.")

    def run_slideshow(self, path: str = "images", verbose: bool = False):
        # Start the slideshow with all present files in subfolder defined in variable 'path'
        try:
            path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / path / "*.*")
            if verbose:
                bash_command = f"sudo fbi --random --blend {self.blend} -a -t {self.timer} -T 1 {path}"
            else:
                bash_command = f"sudo fbi --noverbose --random --blend {self.blend} -a -t {self.timer} -T 1 {path}"

            proc = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            time.sleep(1)
            # module_log.log("Standard output: " + str(stdout))
            module_log.log("Error output: " + str(stderr))
            module_log.log("Slideshow running")
        except Exception as e:
            module_log.log("Exception: " + str(e))

    def restart_slideshow(self, verbose: bool = False):
        # Stop slideshow and restart the slideshow with the new added image files
        module_log.flush_log_file()
        module_log.log("Slideshow restarting")
        self.exit_slideshow()
        self.delete_old_files()
        # Needed implementation for RaspiZeroW to not terminate the start of the framebuffer while booting up
        #time.sleep(2.0)
        self.run_slideshow(verbose=verbose)

    def rise_timer(self, channel):
        # Rise timer of presentation, to lower the showing frequency
        self.timer += 2
        module_log.log(f"Timer raised to: {self.timer}.")
        self.restart_slideshow()

    def lower_timer(self, channel):
        # Lower timer of presentation, to rise the showing frequency
        if self.timer >= 4:
            self.timer -= 2
            module_log.log(f"Timer lowered to: {self.timer}.")
            self.restart_slideshow()
        else:
            module_log.log(f"Timer already at: {self.timer}. Lowering not possible!")

    def system_shutdown(self, channel):
        # Shutdown the whole system
        module_log.log("!!!! SYSTEM IS GOING TO SHUTDOWN !!!!")
        bash_command = f"sudo poweroff"
        subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)
