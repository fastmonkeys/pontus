# -*- coding: utf-8 -*-
import botocore
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
        function that takes Boto S3 Object instance as a parameter.

    :param delete_unvalidated_file:
        Whether to delete the unvalidated file when the new file is copied to new location

    :param new_file_prefix:
        Prefix to be set to the new file that is copied during validation.

    :param new_file_acl:
        Canned ACL set to the new file that is copied during validation.
        Defaults to 'public-read'.

    """
    def __init__(
        self,
        key_name,
        bucket,
        validators=[],
        delete_unvalidated_file=True,
        new_file_prefix='',
        new_file_acl='public-read',
    ):
        self.errors = []
        self.obj = bucket.Object(key_name)
        try:
            self.obj.load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                raise FileNotFoundError(key=key_name)
            else:
                raise e
        self.bucket = bucket
        self.validators = validators
        self.delete_unvalidated_file = delete_unvalidated_file
        self.new_file_prefix = new_file_prefix
        self.new_file_acl = new_file_acl

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
                validator(self.obj)
            except ValidationError as e:
                self.errors.append(e.error)

        if not self.errors and self._has_unvalidated_prefix():
            self._move_to_validated()

        return not self.errors

    def _has_unvalidated_prefix(self):
        return (
            current_app.config.get('AWS_UNVALIDATED_PREFIX') and
            self.obj.key.startswith(
                current_app.config.get('AWS_UNVALIDATED_PREFIX')
            )
        )

    def _move_to_validated(self):
        new_name = self.new_file_prefix + self.obj.key[
            len(current_app.config.get('AWS_UNVALIDATED_PREFIX')):
        ]
        new_obj = self.bucket.Object(new_name)
        new_obj.copy({
            'Bucket': self.bucket.name,
            'Key': self.obj.key
        })
        new_obj.Acl().put(ACL=self.new_file_acl)
        if self.delete_unvalidated_file:
            self.obj.delete()
        self.obj = new_obj

    def __repr__(self):
        return '<{cls} key={key!r}>'.format(
            cls=self.__class__.__name__,
            key=self.obj.key
        )
