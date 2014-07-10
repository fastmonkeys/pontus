# -*- coding: utf-8 -*-
from flask import current_app
from flask.ext.storage import FileNotFoundError

from .exceptions import ValidationError


class AmazonS3FileValidator(object):
    """A Flask-Storage utility for validating files stored in AmazonS3.

    If the Flask application has an `AWS_UNVALIDATED_PREFIX` config, its value
    will be removed from the file key if the file is valid. This enables
    deleting unvalidated files via `Amazon S3 Lifecycle Management`_.

    .. _Amazon S3 Lifecycle Management:
        http://docs.aws.amazon.com/AmazonS3/latest/dev/object-lifecycle-mgmt.html

    Example::

        from flask.ext.storage import FileNotFoundError
        from pontus import AmazonS3FileValidator
        from pontus.validators import MimeType

        try:
            validator = AmazonS3FileValidator(
                key='my/file.jpg',
                storage=storage,
                validators=[MimeType('image/jpeg')]
            )
        except FileNotFoundError:
            # File was not found
            pass

        if validator.validate():
            # File MIME type was image/jpeg
            pass
        else:
            # File was invalid, printing errors
            print validator.errors

    :param key:
        The key of the file stored in Amazon S3.

    :param storage:
        The Flask-Storage S3BotoStorage instance to be used.

    :param validators:
        List of validators. A validator can either be an instance of a class
        inheriting :class:`BaseValidator` or a callable
        function that takes `storage_file` as a parameter.

    """
    def __init__(self, key, storage, validators=[]):
        self.errors = []
        self.file = storage.open(key)
        if not storage.exists(key):
            raise FileNotFoundError()
        self.key = key
        self.storage = storage
        self.validators = validators

    def validate(self):
        """
        Validates the given Amazon S3 file with :attr:`validators`. If errors
        occur they are appended to :attr:`errors`. If the file is valid and a
        `AWS_UNVALIDATED_PREFIX` config is present, its value will be removed
        from the file key.

        :return: a boolean indicating if the file vas valid.
        """
        for validator in self.validators:
            try:
                validator(self.file)
            except ValidationError as e:
                self.errors.append(e.error)

        if not self.errors and self._has_unvalidated_prefix():
            self._move_to_validated()

        return len(self.errors) == 0

    def _has_unvalidated_prefix(self):
        return (
            current_app.config.get('AWS_UNVALIDATED_PREFIX') and
            self.file.name.startswith(
                current_app.config.get('AWS_UNVALIDATED_PREFIX')
            )
        )

    def _move_to_validated(self):
        new_name = self.file.name[
            len(current_app.config.get('AWS_UNVALIDATED_PREFIX')):
        ]
        new_file = self.storage.save(name=new_name, content=self.file.read())
        self.storage.delete(self.file.name)
        self.file = new_file
