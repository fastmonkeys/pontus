# -*- coding: utf-8 -*-
import base64
from datetime import datetime, timedelta
import hmac
import json
import uuid
from hashlib import sha1

from flask import current_app


class AmazonS3SignedRequest(object):
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
        policy = self.get_policy_document()
        return {
            'AWSAccessKeyId': self.storage.access_key,
            'acl': self.storage.acl,
            'key': self.key,
            'Policy': policy,
            'success_action_status': self.success_action_status,
            'Signature': self.get_signature(policy),
        }

    def get_policy_document(self):
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

    def get_signature(self, policy_document):
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
