from PIL import Image

import module_log


class IProc:

    @staticmethod
    def rotate_left(self, image):
        try:
            file = Image.open(image)
            rotated = file.rotate(Image.ROTATE_90)
            rotated.save(image)
            return True
        except Exception as e:
            module_log.log(e)
            return False

    @staticmethod
    def rotate_right(self):
        pass

    @staticmethod
    def transverse(self):
        pass

    @staticmethod
    def transpose(self):
        pass