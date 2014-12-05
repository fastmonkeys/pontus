# -*- coding: utf-8 -*-
from flask import current_app

from .exceptions import FileNotFoundError, ValidationError


class AmazonS3FileValidator(object):
    """A Flask utility for validating files stored in AmazonS3.

    If the application has an `AWS_UNVALIDATED_PREFIX` config, its value
    will be removed from the file key if the file is valid. This enables
    deleting unvalidated files via `Amazon S3 Lifecycle Management`_.

    .. _Amazon S3 Lifecycle Management:
        http://docs.aws.amazon.com/AmazonS3/latest/dev/object-lifecycle-mgmt.html

    Example::

        import boto
        from pontus import AmazonS3FileValidator
        from pontus.exceptions import FileNotFoundError
        from pontus.validators import MimeType

        connection = boto.s3.connection.S3Connection()
        bucket = connection.get_bucket('testbucket')

        try:
            validator = AmazonS3FileValidator(
                key_name='my/file.jpg',
                bucket=bucket,
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

    :param key_name:
        The key of the file stored in Amazon S3.

    :param bucket:
        The Boto S3 Bucket instance.

    :param validators:
        List of validators. A validator can either be an instance of a class
        inheriting :class:`BaseValidator` or a callable
        function that takes Boto S3 Key instance as a parameter.

    """
    def __init__(self, key_name, bucket, validators=[]):
        self.errors = []
        self.key = bucket.get_key(key_name)
        if not self.key:
            raise FileNotFoundError(key=key_name)
        self.bucket = bucket
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
                validator(self.key)
            except ValidationError as e:
                self.errors.append(e.error)

        if not self.errors and self._has_unvalidated_prefix():
            self._move_to_validated()

        return not self.errors

    def _has_unvalidated_prefix(self):
        return (
            current_app.config.get('AWS_UNVALIDATED_PREFIX') and
            self.key.name.startswith(
                current_app.config.get('AWS_UNVALIDATED_PREFIX')
            )
        )

    def _move_to_validated(self):
        new_name = self.key.name[
            len(current_app.config.get('AWS_UNVALIDATED_PREFIX')):
        ]
        new_key = self.key.copy(
            dst_bucket=self.bucket.name,
            dst_key=new_name,
            metadata=None,
            preserve_acl=True
        )
        self.key.delete()
        self.key = new_key

    def __repr__(self):
        return '<{cls} key={key!r}>'.format(
            cls=self.__class__.__name__,
            key=self.key.name
        )
