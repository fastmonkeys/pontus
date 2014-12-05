# -*- coding: utf-8 -*-
class ValidationError(Exception):
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return 'Invalid file: {error}'.format(error=self.error)


class FileNotFoundError(Exception):
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return 'File {key} was not found.'.format(key=self.key)
