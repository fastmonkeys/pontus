# -*- coding: utf-8 -*-
import magic
import re

from ._compat import force_text
from .exceptions import ValidationError


class BaseValidator(object):
    """A base class for validators used with :class:`AmazonS3FileValidator`."""
    def __call__(self, obj):
        """
        Validates an Amazon S3 file.

        :param obj: Boto S3 Object instance to be validated.
        """
        raise NotImplementedError


class MimeType(BaseValidator):
    """Validator for allowing file MIME type(s).

    Uses python-magic to determine MIME type. python-magic depends on
    libmagic library.

    Example::

        from pontus.validators import MimeType

        MimeType('image/jpeg')
        # OR
        MimeType(regex=r"...")
        # OR
        MimeType(mime_types=['image/jpeg', 'image/png'])


    :param mime_type:
        The expected MIME type.

    :param regex:
        A regular expression to match expected MIME type(s).

    :param mime_types:
        A list of expected MIME types. This will override :attr:`mime_type`
        if passed.
    """
    def __init__(self, mime_type=None, regex=None, mime_types=[]):
        if not (mime_type or regex or mime_types):
            raise ValueError(u'No argument for validation provided.')
        self.mime_types = mime_type or mime_types
        self.regex = regex

    def __call__(self, obj):
        """
        Check file MIME type is in :attr:`mime_types` or matches :attr:`regex`.

        :raises ValidationError: if the file MIME type is invalid.
        """
        file_mime_type = force_text(magic.from_buffer(
            obj.get()['Body'].read(), mime=True
        ))

        if self.regex and not re.search(self.regex, file_mime_type):
            raise ValidationError(
                u"File MIME type {mime!s} does not match r'{regex!s}'.".format(
                    mime=file_mime_type,
                    regex=self.regex
                )
            )

        if self.mime_types and (file_mime_type not in self.mime_types):
            raise ValidationError(
                (u"File MIME type is {wrong!s}, not in {right!s}.").format(
                    wrong=file_mime_type,
                    right=self.mime_types
                )
            )

    def __repr__(self):
        mime_types = (
            ' mime_types={types!r}'.format(types=self.mime_types)
            if self.mime_types else ''
        )
        regex = (
            ' regex={regex!r}'.format(regex=self.regex) if self.regex else ''
        )
        return '<{cls}{mime_types}{regex}>'.format(
            cls=self.__class__.__name__, mime_types=mime_types, regex=regex
        )


class DenyMimeType(BaseValidator):
    """Validator for denying file MIME type(s).

    Uses python-magic to determine MIME type. python-magic depends on
    libmagic library.

    Example::

        from pontus.validators import DenyMimeType

        DenyMimeType('image/jpeg')
        # OR
        DenyMimeType(regex=r"...")
        # OR
        DenyMimeType(mime_types=['image/jpeg', 'image/png'])


    :param mime_type:
        The MIME type to deny.

    :param regex:
        A regular expression to match MIME type(s) to deny.

    :param mime_types:
        A list of MIME types to deny. This will override :attr:`mime_type`
        if passed.
    """
    def __init__(self, mime_type=None, regex=None, mime_types=[]):
        if not (mime_type or regex or mime_types):
            raise ValueError(u'No argument for validation provided.')
        self.mime_types = mime_type or mime_types
        self.regex = regex

    def __call__(self, obj):
        """
        Check MIME type is not in :attr:`mime_types` or matches :attr:`regex`.

        :raises ValidationError: if the file MIME type is invalid.
        """
        file_mime_type = force_text(magic.from_buffer(
            obj.get()['Body'].read(), mime=True
        ))

        if self.regex and re.search(self.regex, file_mime_type):
            raise ValidationError(
                u"File MIME type {mime!s} matches denied regex r'{regex!s}'."
                .format(
                    mime=file_mime_type,
                    regex=self.regex
                )
            )

        if self.mime_types and (file_mime_type in self.mime_types):
            raise ValidationError(
                u"File MIME type {mime!s} is in denied list {deny_list!s}."
                .format(
                    mime=file_mime_type,
                    deny_list=self.mime_types
                )
            )

    def __repr__(self):
        mime_types = (
            ' mime_types={types!r}'.format(types=self.mime_types)
            if self.mime_types else ''
        )
        regex = (
            ' regex={regex!r}'.format(regex=self.regex) if self.regex else ''
        )
        return '<{cls}{mime_types}{regex}>'.format(
            cls=self.__class__.__name__, mime_types=mime_types, regex=regex
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

    def __call__(self, obj):
        """
        Check that the file size is between :attr:`min` and :attr:`max`.

        :raises ValidationError: if the file size is invalid.
        """
        if obj.content_length < self.min:
            raise ValidationError(u'File is smaller than %s bytes.' % self.min)
        elif self.max != -1 and obj.content_length > self.max:
            raise ValidationError(u'File is bigger than %s bytes.' % self.max)

    def __repr__(self):
        return '<{cls} min={min!r}, max={max!r}>'.format(
            cls=self.__class__.__name__,
            min=self.min,
            max=self.max
        )
