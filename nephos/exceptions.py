"""
Contains custom errors and exceptions for Nephos
"""


class DBException(Exception):
    """
    Handles exceptions concerning Database
    """
    pass


class SingleInstanceException(BaseException):
    """
    Handles exception raised by SingleInstance class
    """
    pass
