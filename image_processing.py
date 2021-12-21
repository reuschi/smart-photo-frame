from PIL import Image
import module_log
import pathlib


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
