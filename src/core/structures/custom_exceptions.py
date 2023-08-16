import logging


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class RequestErrorException(Exception):
    """Exception raised for errors during request.

    Attributes:
        message -- explanation of the error
        parent -- really catched exception
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
        parent -- really catched exception
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
        parent -- really catched exception
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
        parent -- really catched exception
    """

    def __init__(self, message: str = "Some reading error", parent: Exception = None):
        self.message = message
        self.parent = parent
        logger.error(f'ReadingErrorException\n{message}\n{parent}')
        super().__init__(self.message)


class DataBaseErrorException(Exception):
    """Exception raised for errors during request.

    Attributes:
        message -- explanation of the error
        parent -- really catched exception
    """

    def __init__(self, message: str="Some database error", parent: Exception=None):
        self.message = message
        self.parent = parent
        logger.error(f'DataBaseErrorException\n{message}\n{parent}')
        super().__init__(self.message)
