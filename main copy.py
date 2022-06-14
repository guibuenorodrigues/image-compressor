import argparse
import os
from time import sleep

from PIL import Image
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver as Observer

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
        self.__locked_file_size_bytes: int = 0

        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f'file {self.file_path} not exists')

        if not self.is_acceptable():
            raise ValueError(
                f'extension **{self.extension}** is not in the accepted list: {self.__ACCEPTED_EXTENSIONS}'
            )

    def get_extension(self) -> str:
        """return the file extention from a given path"""

        return self.file_path.split('.')[-1]

    def is_acceptable(self) -> bool:
        """return if extension is acceptable or not"""

        return self.get_extension() in self.__ACCEPTED_EXTENSIONS

    def is_locked(self) -> bool:
        locked = False

        try:
            with open(self.file_path, 'r') as file:

                file.seek(0, os.SEEK_END)
                size = file.tell()

                self.logger.info('current size: %d', size)
                self.logger.info(
                    'last size read: %d', self.__locked_file_size_bytes
                )

                if size < 0 or self.__locked_file_size_bytes < size:
                    self.__locked_file_size_bytes = size
                    locked = True
        except IOError:
            locked = True
        except Exception:
            locked = True

        return locked

    def wait_unlock_file(self) -> None:

        self.logger.info('waiting file to unlock')

        wait_time_sec = 2
        max_wait_time_sec = 600
        elapsed_time_sec = 0

        while self.is_locked():
            if elapsed_time_sec > max_wait_time_sec:
                raise TimeoutError(
                    f'file is blocked for more than max time {max_wait_time_sec}'
                )

            sleep(wait_time_sec)
            elapsed_time_sec += 1

        self.logger.info('file unlocked and ready to be used')

    def compress(
        self,
        optimize: bool = True,
        quality: int = 100,
        wait_unlock: bool = True,
    ):
        """compress the image from a given path"""
        try:
            if wait_unlock:
                self.wait_unlock_file()

            image = Image.open(self.file_path)

            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')

            image.save(self.file_path, optimize=optimize, quality=quality)

            self.compressed_size_bytes = os.stat(self.file_path).st_size
            self.compressed_percentage = round(
                (1 - (self.compressed_size_bytes / self.original_size_bytes)),
                2,
            )
        except TimeoutError:
            self.logger.exception('timeout to open file. %s', self.file_path)


# class Watcher:
#     """class to enable the watcher"""

#     def __init__(self, directory: str, handler=FileSystemEventHandler) -> None:
#         self.logger = get_logger(__name__)
#         self.observer = Observer()
#         self.handler = handler
#         self.directory: str = directory

#     def run(self, recursive: str = False) -> None:
#         """run the watcher to monitor the events on a given directory"""

#         self.observer.schedule(
#             event_handler=self.handler,
#             path=self.directory,
#             recursive=recursive,
#         )

#         self.observer.start()
#         self.logger.info(
#             'watcher has started in [%s] directory', self.directory
#         )

#         try:
#             while True:
#                 sleep(1)
#         except KeyboardInterrupt:
#             self.logger.warning('Keyboard has interrupted the watcher')
#         except Exception as err:
#             raise Exception(
#                 'an error occurred during the watcher execution'
#             ) from err
#         finally:
#             self.observer.unschedule_all()
#             self.observer.stop()
#             self.logger.info('watcher has been stopped successfuly')

#         self.observer.join()
#         self.logger.info('watcher has terminated')


# class EventsHandler(FileSystemEventHandler):
#     """class to handle the events"""

#     def __init__(self, quality: int = None) -> None:
#         super().__init__()
#         self.logger = get_logger(__name__)
#         self.file_path: str = None
#         self.quality: int = 50 if quality is None else quality
#         self.logger.info(
#             'image quality after compression defined to %d', self.quality
#         )

#     def work_on_file(self) -> None:
#         """work on the file that have triggered the event"""

#         try:
#             img_handler = ImageHandler(self.file_path)
#             img_handler.compress(quality=self.quality)


#             self.logger.info(
#                 '[%s] has been compressed. from %d bytes to %d bytes. Reduce of %s',
#                 img_handler.file_path,
#                 img_handler.original_size_bytes,
#                 img_handler.compressed_size_bytes,
#                 '{:.2%}'.format(img_handler.compressed_percentage),
#             )

#         except ValueError as err:
#             self.logger.warning(err)
#         except Exception:
#             self.logger.exception('error to work on file')

#     def on_created(self, event):
#         """triggered on a file is created"""

#         if event.is_directory:
#             return

#         self.file_path = event.src_path
#         self.logger.debug('file has been created on %s', self.file_path)

#         self.work_on_file()


class Watcher:
    def __init__(self, directory: str, quality: int) -> None:
        self.logger = get_logger(__name__)
        self.directory = directory
        self.quality = quality
        self.control_file = '.compressed'
        self.logger.info('directory to watch: %s', self.directory)
        self.logger.info(
            'image quality after compression defined to %d', self.quality
        )

    def run(self) -> None:

        for file in os.listdir(self.directory):
            try:
                full_path = os.path.join(self.directory, file)

                if os.path.isdir(full_path):
                    continue

                image = ImageHandler(full_path)
                image.compress(quality=self.quality, wait_unlock=False)

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
            except Exception as err:
                self.logger.exception(
                    'error to compress file. [%s]', full_path
                )
                self.logger.info('skip and move to the next file')


def main():
    """function called if the __name__ is equal to __main__"""
    parser = argparse.ArgumentParser(
        description='watch directory and compress images', exit_on_error=True
    )
    parser.add_argument(
        '-d',
        '--directory',
        help='directory to be watched (str)',
        default='.',
        type=str,
    )
    parser.add_argument(
        '-q',
        '--quality',
        help='the quality of the image after compressions. 0 = low, 100 = high (int)',
        default=100,
        type=int,
    )
    parser.add_argument(
        '-D',
        '--debug',
        help='enable or not debug logging (str)',
        default='False',
        type=str,
    )
    parser.add_argument(
        '-I',
        '--interval',
        help='provide the interval in seconds between each files lookup',
        default='180',
        type=int,
    )

    args = parser.parse_args()

    directory = args.directory
    quality = (
        args.quality if args.quality >= 0 and args.quality <= 100 else 100
    )
    debug = (
        True if args.debug.lower() in ['true', 'True', '1', 'yes'] else False
    )
    interval = args.interval

    os.environ.setdefault('DEBUG', str(debug))

    logger = get_logger(__name__)
    logger.info('application has started and configured')
    logger.info('DEBUG MODE: %s', os.getenv('DEBUG'))
    logger.info('lookup internval: %d', interval)

    logger.debug('args.parse_args: %s', args)

    try:
        while True:
            watcher = Watcher(directory, quality)
            watcher.run()

            logger.info('waiting next lookup interval in %d seconds', interval)

            sleep(interval)

            logger.info('looking up again')

    except KeyboardInterrupt:
        logger.warning('Keyboard has interrupted the watcher')
    except Exception as err:
        raise Exception(
            'an error occurred during the watcher execution'
        ) from err

    logger.info('application has terminated')


if __name__ == '__main__':
    main()
