""" Processing images on the SD Card """

from pathlib import Path
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
            path = Path(Path(__file__).parent.absolute() / "images" / image.lower())
            file = Image.open(path)
            if orientation == "l":
                file = IProc.__rotate_left(file)
            elif orientation == "r":
                file = IProc.__rotate_right(file)
            elif orientation == "tv":
                pass
            elif orientation == "tp":
                pass
            elif orientation == "check":
                if IProc.check_orientation(path):
                    return "Ok"
            else:
                file = file.rotate(0, expand=True)

            file.save(path)
            file.close()
            return "Ok"
        except FileNotFoundError:
            module_log.log(f"No such file or directory: {image}")
            return f"No such file or directory: {image}"
        except Exception as exc:
            module_log.log(exc)
            return exc

    @staticmethod
    def check_orientation(image_path):
        """ Check if image is oriented portrait and needs to be rotated """

        success = False

        try:
            path = str(image_path)
            file = Image.open(path)

            # Read EXIF data from image
            exif_data = file.getexif()

            if exif_data.get(274) and exif_data[274] == 6:
                module_log.log(f"Orientation of {image_path.name} is portrait and needs to be "
                               f"rotated right.")
                file = IProc.__rotate_right(file)
                file.save(path)
                success = True
            elif exif_data.get(274) and exif_data[274] == 8:
                module_log.log(f"Orientation of {image_path.name} is portrait and needs to be "
                               f"rotated left.")
                file = IProc.__rotate_left(file)
                file.save(path)
                success = True
            elif exif_data.get(274):
                module_log.log(f"Orientation of {image_path.name} is landscape; no rotation "
                               f"needed.")
            else:
                module_log.log(f"Orientation of {image_path.name} can't be catched; no rotation "
                               f"needed.")

            file.close()
            #return "Ok"
        except AttributeError:
            # Exception if EXIF data not present in image file
            module_log.log(f"Orientation of {image_path.name} can't be catched; no rotation "
                           f"needed.")
        except KeyError:
            # Exception if EXIF data not present in image file
            module_log.log(f"Orientation of {image_path.name} can't be catched; no rotation "
                           f"needed.")
        except Exception as exc:
            module_log.log(f"Exception: {exc} of type {type(exc)}")

        return success

    @staticmethod
    def check_all_file_orientation(image_path="images"):
        """ Check orientation of all image files in folder and correct if needed """

        try:
            path = Path(Path(__file__).parent.absolute() / image_path.lower())

            return_value = False
            counter = 0

            for file in path.glob('**/*'):
                if file.is_file():
                    return_value = IProc.check_orientation(file)
                    if return_value:
                        counter += 1

            return counter
        except Exception as exc:
            return exc

    @staticmethod
    def delete_image(image: str):
        """ Delete an image """

        try:
            image_file = Path(Path(__file__).parent.absolute() / "images" / image)
            bash_command = f"sudo rm {image_file}"
            with subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as reply:
                _stdout, stderr = reply.communicate()
            encoding = 'utf-8'
            return str(stderr, encoding)
        except FileNotFoundError:
            return f"No such file or directory: {image}"
