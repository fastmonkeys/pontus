# -*- coding: utf-8 -*-
import magic

from .exceptions import ValidationError


class AmazonS3FileValidator(object):
    def __call__(self, storage_file):
        raise NotImplementedError


class MimeType(AmazonS3FileValidator):
    def __init__(self, mime_type):
        self.mime_type = mime_type

    def __call__(self, storage_file):
        file_mime_type = magic.from_buffer(storage_file.read(), mime=True)
        if file_mime_type != self.mime_type:
            raise ValidationError(
                u"File MIME type is '%s', not '%s'." % (
                    file_mime_type,
                    self.mime_type
                )
            )


class FileSize(AmazonS3FileValidator):
    def __init__(self, min=-1, max=-1):
        if not (min != -1 or max != -1):
            raise ValueError(
                u'At least one of `min` or `max` must be defined.'
            )
        if not (max == -1 or min <= max):
            raise ValueError(u'Argument `min` cannot be more than `max`.')
        self.min = min
        self.max = max

    def __call__(self, storage_file):
        if storage_file.size < self.min:
            raise ValidationError(u'File is smaller than %s bytes.' % self.min)
        elif self.max != -1 and storage_file.size > self.max:
            raise ValidationError(u'File is bigger than %s bytes.' % self.max)
