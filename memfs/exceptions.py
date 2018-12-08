"""
This file contains the exceptions raised by the memfs library
"""


class PathNotFoundException(Exception):
    pass


class PathAlreadyExistsException(Exception):
    pass


class IllegalFileSystemOperation(Exception):
    pass


class InvalidWriteException(Exception):
    pass
