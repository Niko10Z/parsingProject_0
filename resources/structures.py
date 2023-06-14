from typing import List, IO, NamedTuple
from datetime import datetime
import logging
import os


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))[:-10]
conf_log_filename = 'pars_log.txt'
conf_last_parsing_dt_filename = 'last_parsing.txt'


logging.basicConfig(filename=os.path.join(ROOT_DIR, conf_log_filename),
                    filemode='a',
                    format='%(asctime)s %(name)s %(levelname)s \n%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ArticleInfo(NamedTuple):
    header: str
    content: str
    publication_dt: datetime
    parsing_dt: datetime
    html: str
    href: str
    language: str


class ArticleShortInfo(NamedTuple):
    category: str
    title: str
    link: str
    description: str
    author: str
    pub_datetime: datetime


class RequestErrorException(Exception):
    """Exception raised for errors during request.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str="Some requesting error", parent: Exception=None):
        self.message = message
        self.parent = parent
        logger.error(f'RequestErrorException\n{message}\n{parent}')
        super().__init__(self.message)


class ParsingErrorException(Exception):
    """Exception raised for errors in parsing.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str = "Some parsing error", parent: Exception = None):
        self.message = message
        self.parent = parent
        logger.error(f'ParsingErrorException\n{message}\n{parent}')
        super().__init__(self.message)


class SavingErrorException(Exception):
    """Exception raised for errors in saving.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str = "Some saving error", parent: Exception = None):
        self.message = message
        self.parent = parent
        logger.error(f'SavingErrorException\n{message}\n{parent}')
        super().__init__(self.message)


class ReadingErrorException(Exception):
    """Exception raised for errors in reading from file.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str = "Some reading error", parent: Exception = None):
        self.message = message
        self.parent = parent
        logger.error(f'ReadingErrorException\n{message}\n{parent}')
        super().__init__(self.message)
