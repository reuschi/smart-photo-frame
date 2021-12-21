from PIL import Image
import module_log
import pathlib
import subprocess


class IProc:

    @staticmethod
    def __rotate_left(file: Image) -> Image:
        try:
            rotated = file.rotate(90, expand=True)
            return rotated
        except Exception as e:
            module_log.log(e)
            return None

    @staticmethod
    def __rotate_right(file: Image) -> Image:
        try:
            rotated = file.rotate(270, expand=True)
            return rotated
        except Exception as e:
            module_log.log(e)
            return None

    @staticmethod
    def transverse(image: str):
        pass

    @staticmethod
    def transpose(image: str):
        pass

    @staticmethod
    def rotate(image: str, orientation: str):
        try:
            path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "images" / image.lower())
            file = Image.open(path)
            if orientation == "l":
                rotated = IProc.__rotate_left(file)
            elif orientation == "r":
                rotated = IProc.__rotate_right(file)
            elif orientation == "tv":
                pass
            elif orientation == "tp":
                pass
            else:
                rotated = file.rotate(0, expand=True)

            rotated.save(path)
            return "Ok"
        except FileNotFoundError:
            module_log.log(f"No such file or directory: {image}")
            return f"No such file or directory: {image}"
        except Exception as e:
            module_log.log(e)
            return e

    @staticmethod
    def delete_image(image: str):
        try:
            image_file = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "images" / image)
            bash_command = f"sudo rm {image_file}"
            reply = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = reply.communicate()
            
            return stderr
        except FileNotFoundError:
            return f"No such file or directory: {image}"

