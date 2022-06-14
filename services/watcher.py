import json
import os
from typing import Optional

from services.image_handler import ImageHandler
from utils.logger import get_logger


class Watcher:
    """watch the directory"""

    def __init__(self, directory: str, quality: int) -> None:
        self.logger = get_logger(__name__)
        self.directory = directory
        self.quality = quality
        self.control_file = os.path.join(self.directory, '.compressed.json')
        self.logger.info('directory to watch: %s', self.directory)
        self.logger.info(
            'image quality after compression defined to %d', self.quality
        )

    def get_image_data_from_json(self, file: str) -> Optional[dict]:

        data = self.read_json()

        if data is None or file not in data:
            self.logger.debug('data is none or file is not in data')
            return None

        return data[file]

    def get_image_size_from_json(self, file: str) -> Optional[int]:

        data = self.get_image_data_from_json(file)

        if (
            data is None
            or 'size' not in data
            or not isinstance(data['size'], int)
        ):
            self.logger.debug(
                'size is none or size is not in data or size is not int '
            )
            return None

        return data['size']

    def read_json(self) -> Optional[dict]:

        data = None
        if os.path.exists(self.control_file):
            with open(self.control_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
        return data

    def save_to_json(self, file: str, size: int, extension: str) -> None:

        data = self.read_json()

        if data is None:
            data = {
                file: {
                    'path': os.path.join(
                        self.directory,
                        file,
                    ),
                    'size': size,
                    'extension': extension,
                }
            }

        else:
            data[file] = {
                'path': os.path.join(
                    self.directory,
                    file,
                ),
                'size': size,
                'extension': extension,
            }

        with open(self.control_file, 'w', encoding='utf-8') as file:
            json.dump(data, file)

    def run(self) -> None:
        """run the process to find the file that needs to be compressed"""

        for file in os.listdir(self.directory):
            self.logger.debug('working on file %s in %s', file, self.directory)

            full_path = os.path.join(self.directory, file)

            if os.path.isdir(full_path):
                self.logger.debug('%s is not a file', full_path)
                continue

            try:
                image = ImageHandler(full_path)

                # check if image is a json file and ignore if it's
                if image.extension == 'json':
                    self.logger.debug(
                        'ignoring json file because it is the control file'
                    )
                    continue

                # get the last size to use as comparasion in the process
                last_size = self.get_image_size_from_json(file)

                if (
                    last_size is not None
                    and image.original_size_bytes <= last_size
                ):
                    self.logger.debug(
                        'image size is less or equal to last size'
                    )
                    self.logger.debug('moving to next file')
                    continue

                # compress the image itself
                image.compress(quality=self.quality)

                # save compression data to json control
                self.save_to_json(
                    file, image.compressed_size_bytes, image.extension
                )

                self.logger.info(
                    '[%s] has been compressed. from %d bytes to %d bytes. Reduce of %s',
                    image.file_path,
                    image.original_size_bytes,
                    image.compressed_size_bytes,
                    '{:.2%}'.format(image.compressed_percentage),
                )
            except ValueError as err:
                self.logger.warning('error to compress file [%s]', full_path)
                self.logger.exception(err)
                self.logger.info('skip and move to the next file')
                continue
            except Exception as err:
                self.logger.exception(
                    'error to compress file. [%s]', full_path
                )
                self.logger.info('skip it and move to the next file')
                continue
