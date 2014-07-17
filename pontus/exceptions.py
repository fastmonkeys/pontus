# -*- coding: utf-8 -*-
class ValidationError(Exception):
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return 'Invalid file: {error}'.format(error=self.error)


class MisconfiguredError(Exception):
    def __init__(self, attrs):
        self.attrs = attrs

    def __str__(self):
        return (
            'Flask-Storage instance missing attributes for AWS. ' +
            'Missing attributes: {attrs}.'
        ).format(attrs=', '.join(self.attrs))
