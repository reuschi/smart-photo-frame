from PIL import Image
import module_log
import pathlib


class IProc:

    @staticmethod
    def rotate_left(image):
        try:
            path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "images" / image)
            file = Image.open(path)
            rotated = file.rotate(90, expand=True)
            rotated.save(path)
            return True
        except Exception as e:
            module_log.log(e)
            return False

    @staticmethod
    def rotate_right(image):
        pass

    @staticmethod
    def transverse(image):
        pass

    @staticmethod
    def transpose(image):
        pass