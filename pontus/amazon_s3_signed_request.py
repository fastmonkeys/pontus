# -*- coding: utf-8 -*-
import base64
from datetime import datetime, timedelta
import hmac
import json
import uuid
from hashlib import sha1

from flask import current_app


class AmazonS3SignedRequest(object):
    """A Flask-Storage utility for creating signatures for
    `POST requests to Amazon S3`_.

    .. _POST requests to Amazon S3:
        http://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-authentication-HTTPPOST.html

    If the Flask application has an `AWS_UNVALIDATED_PREFIX` config, its value
    will be added to the file key.

    Example::

        from pontus import AmazonS3SignedRequest

        signed_request = AmazonS3SignedRequest(
            key=u'my/file.jpg',
            mime_type=u'image/jpeg',
            storage=storage,
        )

        assert signed_request.form_fields == {
            'AWSAccessKeyId': 'your-flask-storage-aws-access-key',
            'acl': 'your-flask-storage-acl',
            'key': 'my/file.jpg',
            'Policy': 'generated-policy-document',
            'success_action_status': '201',
            'Signature': 'generated-signature',
        }

    :param key:
        The key of the file to be stored in Amazon S3.

    :param mime_type:
        The MIME type of the file to be stored in Amazon S3.

    :param storage:
        The Flask-Storage S3BotoStorage instance to be used.

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
        key,
        mime_type,
        storage,
        expires_in=60,
        success_action_status='201',
        max_content_length=None,
        randomize=False
    ):
        if randomize:
            key = u'%s/%s' % (uuid.uuid4(), key)

        key = u'%s%s' % (
            current_app.config.get('AWS_UNVALIDATED_PREFIX', ''),
            key
        )

        self.expires_in = expires_in
        self.key = key
        self.max_content_length = (
            max_content_length or
            current_app.config.get('MAX_CONTENT_LENGTH') or
            20971520
        )
        self.mime_type = mime_type
        self.randomize = randomize
        self.storage = storage
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
            'AWSAccessKeyId': self.storage.access_key,
            'acl': self.storage.acl,
            'key': self.key,
            'Policy': policy,
            'success_action_status': self.success_action_status,
            'Signature': self._get_signature(policy),
        }

    def _get_policy_document(self):
        expiration = datetime.utcnow() + timedelta(seconds=self.expires_in)
        data = {
            'expiration': expiration.isoformat() + 'Z',
            'conditions': [
                {'bucket': self.storage.bucket_name},
                {'key': self.key},
                {'acl': self.storage.acl},
                ['starts-with', '$Content-Type', ''],
                ['content-length-range', 0, self.max_content_length],
                {'success_action_status': self.success_action_status}
            ]
        }
        data = json.dumps(data)
        return base64.b64encode(data)

    def _get_signature(self, policy_document):
        return base64.encodestring(hmac.new(
            self.storage.secret_key,
            policy_document,
            sha1
        ).digest()).strip()

    def __repr__(self):
        return '<{cls} key={key!r}>'.format(
            cls=self.__class__.__name__,
            key=self.key
        )

    def __unicode__(self):
        return self.key
