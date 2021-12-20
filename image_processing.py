from PIL import Image
import module_log
import pathlib


class IProc:

    @staticmethod
    def rotate_left(image: str):
        try:
            path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "images" / image.lower())
            file = Image.open(path)
            rotated = file.rotate(90, expand=True)
            rotated.save(path)
            return True
        except Exception as e:
            module_log.log(e)
            return False

    @staticmethod
    def rotate_right(image: str):
        try:
            path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "images" / image.lower())
            file = Image.open(path)
            rotated = file.rotate(270, expand=True)
            rotated.save(path)
            return True
        except Exception as e:
            module_log.log(e)
            return False

    @staticmethod
    def transverse(image: str):
        pass

    @staticmethod
    def transpose(image: str):
        pass