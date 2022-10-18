""" Processing images on the SD Card """

import pathlib
import subprocess

from PIL import Image
import module_log


class IProc:
    """ Stored images can be rotated, transversed or transposed """

    @staticmethod
    def __rotate_left(file: Image) -> Image:
        """ Rotate image 90 degrees left """
        try:
            rotated = file.rotate(90, expand=True)
            return rotated
        except Exception as exc:
            module_log.log(exc)
            return None

    @staticmethod
    def __rotate_right(file: Image) -> Image:
        """ Rotate image 90 degrees right """
        try:
            rotated = file.rotate(270, expand=True)
            return rotated
        except Exception as exc:
            module_log.log(exc)
            return None

    @staticmethod
    def transverse(image: str):
        """ Transverse image """

    @staticmethod
    def transpose(image: str):
        """ Transpose image """

    @staticmethod
    def rotate(image: str, orientation: str):
        """ Depending on the orientation, the image can be rotated left or right """
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
        except Exception as exc:
            module_log.log(exc)
            return exc

    @staticmethod
    def delete_image(image: str):
        """ Delete an image """
        try:
            image_file = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "images" / image)
            bash_command = f"sudo rm {image_file}"
            reply = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
            _stdout, stderr = reply.communicate()
            encoding = 'utf-8'
            return str(stderr, encoding)
        except FileNotFoundError:
            return f"No such file or directory: {image}"
