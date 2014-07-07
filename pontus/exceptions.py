# -*- coding: utf-8 -*-
class ValidationError(Exception):
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return 'ValidationError: {error}'.format(error=self.error)
