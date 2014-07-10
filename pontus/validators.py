# -*- coding: utf-8 -*-
import magic

from .exceptions import ValidationError


class BaseValidator(object):
    """A base class for validators used with :class:`AmazonS3FileValidator`."""
    def __call__(self, storage_file):
        """
        Validates an Amazon S3 file.

        :param storage_file: Flask-Storage S3BotoStorageFile to be validated.
        """
        raise NotImplementedError


class MimeType(BaseValidator):
    """Validator for file MIME type.

    Uses python-magic to determine MIME type. python-magic depends on
    libmagic library.

    Example::

        from pontus.validators import MimeType

        MimeType('image/jpeg')


    :param mime_type:
        The expected MIME type.

    """
    def __init__(self, mime_type):
        self.mime_type = mime_type

    def __call__(self, storage_file):
        """
        Check that the file MIME type is :attr:`mime_type`.

        :raises ValidationError: if the file MIME type is invalid.
        """
        file_mime_type = magic.from_buffer(storage_file.read(), mime=True)
        if file_mime_type != self.mime_type:
            raise ValidationError(
                u"File MIME type is '%s', not '%s'." % (
                    file_mime_type,
                    self.mime_type
                )
            )


class FileSize(BaseValidator):
    """Validator for file size.

    Example::

        from pontus.validators import FileSize

        FileSize(min=1024, max=2048)


    :param min:
        The minimum file size in bytes.

    :param max:
        The maximum file size in bytes.

    """
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
        """
        Check that the file size is between :attr:`min` and :attr:`max`.

        :raises ValidationError: if the file size is invalid.
        """
        if storage_file.size < self.min:
            raise ValidationError(u'File is smaller than %s bytes.' % self.min)
        elif self.max != -1 and storage_file.size > self.max:
            raise ValidationError(u'File is bigger than %s bytes.' % self.max)
