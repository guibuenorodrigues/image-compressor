import os

from PIL import Image, UnidentifiedImageError

from utils.logger import get_logger


class ImageHandler:
    """class to handle images"""

    __ACCEPTED_EXTENSIONS = ['jpeg', 'jpg', 'png']

    def __init__(self, file_path: str) -> None:
        self.logger = get_logger(__name__)
        self.file_path = file_path
        self.original_size_bytes: int = os.stat(self.file_path).st_size
        self.extension: str = self.get_extension()
        self.compressed_size_bytes: int = 0
        self.compressed_percentage: float = 0.0

        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f'file {self.file_path} not exists')

    def get_extension(self) -> str:
        """return the file extention from a given path"""

        return self.file_path.split('.')[-1]

    def is_acceptable(self) -> bool:
        """return if extension is acceptable or not"""

        return self.get_extension() in self.__ACCEPTED_EXTENSIONS

    def compress(self, optimize: bool = True, quality: int = 100):
        """compress the image from a given path"""

        if not self.is_acceptable():
            raise ValueError(
                f'extension **{self.extension}** is not in the accepted list: {self.__ACCEPTED_EXTENSIONS}'
            )

        try:

            image = Image.open(self.file_path)

            # if image is RGBA we need to convert it to RGB
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')

            image.save(self.file_path, optimize=optimize, quality=quality)

            self.compressed_size_bytes = os.stat(self.file_path).st_size
            self.compressed_percentage = round(
                (1 - (self.compressed_size_bytes / self.original_size_bytes)),
                2,
            )
        except UnidentifiedImageError as err:
            self.logger.warning(err)
