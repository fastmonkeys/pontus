# -*- coding: utf-8 -*-
import base64
import hmac
import json
import uuid
from datetime import datetime, timedelta
from hashlib import sha1

from flask import current_app

from ._compat import force_bytes, force_text, unicode_compatible


@unicode_compatible
class AmazonS3SignedRequest(object):
    """A Flask utility for creating signatures for
    `POST requests to Amazon S3`_.

    .. _POST requests to Amazon S3:
        http://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-authentication-HTTPPOST.html

    If the application has an `AWS_UNVALIDATED_PREFIX` config, its value
    will be added to the file key.

    Example::

        import boto
        from pontus import AmazonS3SignedRequest

        connection = boto.s3.connection.S3Connection()
        bucket = connection.get_bucket('testbucket')

        signed_request = AmazonS3SignedRequest(
            key_name=u'my/file.jpg',
            mime_type=u'image/jpeg',
            bucket=bucket,
        )

        assert signed_request.form_fields == {
            'AWSAccessKeyId': 'your-aws-access-key',
            'acl': 'public-read',
            'key': 'my/file.jpg',
            'Policy': 'generated-policy-document',
            'success_action_status': '201',
            'Signature': 'generated-signature',
        }

    :param key_name:
        The key name of the file to be stored in Amazon S3.

    :param mime_type:
        The MIME type of the file to be stored in Amazon S3.

    :param bucket:
        The Boto Bucket instance to be used.

    :param acl:
        The ACL of the uploaded file, for example 'public-read' or 'private'.

    :param expires_in:
        The expiry time of the signature.

    :param success_action_status:
        Status code Amazon S3 should respond with on successful POST.

    :param max_content_length:
        The maximum length of the file to be stored.

    :param randomize:
        Indicates if a randomized UUID prefix should be added to the file key.
    """
    def __init__(
        self,
        key_name,
        mime_type,
        bucket,
        acl='public-read',
        expires_in=60,
        success_action_status='201',
        max_content_length=None,
        randomize=False,
    ):
        if randomize:
            key_name = u'%s/%s' % (uuid.uuid4(), key_name)

        key_name = u'%s%s' % (
            current_app.config.get('AWS_UNVALIDATED_PREFIX', ''),
            key_name
        )

        self.expires_in = expires_in
        self.key_name = key_name
        self.acl = acl
        self.max_content_length = (
            max_content_length or
            current_app.config.get('MAX_CONTENT_LENGTH') or
            20971520
        )
        self.mime_type = mime_type
        self.randomize = randomize
        self.bucket = bucket
        self.success_action_status = success_action_status

    @property
    def form_fields(self):
        """
        Generates form fields needed for creating a signed POST request to
        Amazon S3.

        :return: a dictionary containing the needed field values
        """
        policy = self._get_policy_document()
        return {
            'AWSAccessKeyId': self.bucket.connection.aws_access_key_id,
            'acl': self.acl,
            'key': self.key_name,
            'Policy': policy,
            'success_action_status': self.success_action_status,
            'Signature': self._get_signature(policy),
        }

    def _get_policy_document(self):
        expiration = datetime.utcnow() + timedelta(seconds=self.expires_in)
        data = {
            'expiration': expiration.isoformat() + 'Z',
            'conditions': [
                {'bucket': self.bucket.name},
                {'key': self.key_name},
                {'acl': self.acl},
                ['starts-with', '$Content-Type', ''],
                ['content-length-range', 0, self.max_content_length],
                {'success_action_status': self.success_action_status}
            ]
        }
        data = json.dumps(data)
        return force_text(base64.b64encode(force_bytes(data)))

    def _get_signature(self, policy_document):
        signature = base64.encodestring(hmac.new(
            force_bytes(self.bucket.connection.aws_secret_access_key),
            force_bytes(policy_document),
            sha1
        ).digest()).strip()
        return force_text(signature)

    def __repr__(self):
        return "<{cls} key_name='{key_name!s}'>".format(
            cls=self.__class__.__name__,
            key_name=self.key_name
        )

    def __str__(self):
        return self.key_name
