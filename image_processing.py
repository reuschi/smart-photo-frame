from PIL import Image
import module_log
import pathlib


class IProc:

    @staticmethod
    def rotate_left(image: str):
        '''
        try:
            path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "images" / image.lower())
            file = Image.open(path)
            #rotated = file.rotate(90, expand=True)
            #rotated.save(path)
            return True
        except Exception as e:
            module_log.log(e)
            return False
        '''
        #return IProc.__rotate(image, "l")
        if IProc.__rotate(image, "l"):
            module_log.log(f"Image {image} rotated left.")
            return True
        else:
            return False

    @staticmethod
    def rotate_right(image: str):
        '''
        try:
            path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "images" / image.lower())
            file = Image.open(path)
            rotated = file.rotate(270, expand=True)
            rotated.save(path)
            return True
        except Exception as e:
            module_log.log(e)
            return False
        '''
        if IProc.__rotate(image, "r"):
            module_log.log(f"Image {image} rotated left.")
            return True
        else:
            return False

    @staticmethod
    def transverse(image: str):
        return IProc.__rotate(image, "tv")

    @staticmethod
    def transpose(image: str):
        return IProc.__rotate(image, "tr")

    @staticmethod
    def __rotate(image: str, orientation: str):
        try:
            path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "images" / image.lower())
            file = Image.open(path)
            if orientation == "l":
                rotated = file.rotate(90, expand=True)
            elif orientation == "r":
                rotated = file.rotate(270, expand=True)
            elif orientation == "tv":
                pass
            elif orientation == "tp":
                pass
            else:
                rotated = file.rotate(0, expand=True)

            rotated.save(path)
            return True
        except FileNotFoundError:
            module_log.log(f"No such file or directory: {image}")
            return False
        except Exception as e:
            module_log.log(e)
            return False
