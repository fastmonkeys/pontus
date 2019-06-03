# -*- coding: utf-8 -*-
import base64
import binascii
import hmac
import json
import uuid
from datetime import datetime, timedelta
from hashlib import sha256

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
            'Content-Type': 'image/png',
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

    service_name = 's3'
    salt = 'aws4_request'
    algorithm = 'AWS4-HMAC-SHA256'

    def __init__(
        self,
        key_name,
        mime_type,
        bucket,
        session,
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
        self.session = session
        self.success_action_status = success_action_status

    @property
    def form_fields(self):
        """
        Generates form fields needed for creating a signed POST request to
        Amazon S3.

        :return: a dictionary containing the needed field values
        """
        date = datetime.utcnow()
        policy = self._get_policy_document(date)
        return {
            'acl': self.acl,
            'Content-Type': self.mime_type,
            'key': self.key_name,
            'policy': policy,
            'x-amz-algorithm': self.algorithm,
            'x-amz-credential': self._get_credential(date),
            'x-amz-date': date.strftime('%Y%m%dT%H%M%SZ'),
            'success_action_status': self.success_action_status,
            'x-amz-signature': self._get_signature(date, policy),
        }

    def _get_credential(self, date):
        return '/'.join([
            self.session.get_credentials().access_key,
            date.strftime('%Y%m%d'),
            self.session.region_name,
            self.service_name,
            self.salt
        ])

    def _get_policy_document(self, date):
        expiration = datetime.utcnow() + timedelta(seconds=self.expires_in)
        data = {
            'expiration': expiration.isoformat() + 'Z',
            'conditions': [
                {'x-amz-algorithm': self.algorithm},
                {'x-amz-credential': self._get_credential(date)},
                {'x-amz-date': date.strftime('%Y%m%dT%H%M%SZ')},
                {'bucket': self.bucket.name},
                {'key': self.key_name},
                {'acl': self.acl},
                {'Content-Type': self.mime_type},
                ['content-length-range', 0, self.max_content_length],
                {'success_action_status': self.success_action_status}
            ]
        }
        data = json.dumps(data)
        return force_text(base64.b64encode(force_bytes(data)))

    def _sign(self, key, msg):
        return hmac.new(
            key,
            msg.encode('utf-8'),
            sha256
        ).digest()

    def _get_signing_key(self, date):
        # Variable naming from the documentation
        # https://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html
        key = self.session.get_credentials().secret_key
        dateStamp = date.strftime('%Y%m%d')
        regionName = self.session.region_name
        serviceName = self.service_name
        salt = self.salt

        kSecret = ('AWS4' + key).encode('utf-8')
        kDate = self._sign(kSecret, dateStamp)
        kRegion = self._sign(kDate, regionName)
        kService = self._sign(kRegion, serviceName)
        kSigning = self._sign(kService, salt)
        return kSigning

    def _get_signature(self, date, policy_document):
        signing_key = self._get_signing_key(date)
        return force_text(binascii.hexlify(self._sign(signing_key, policy_document)))

    def __repr__(self):
        return "<{cls} key_name='{key_name!s}'>".format(
            cls=self.__class__.__name__,
            key_name=self.key_name
        )

    def __str__(self):
        return self.key_name
