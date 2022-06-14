import argparse
import os
from time import sleep

from services.watcher import Watcher
from utils.logger import get_logger


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
