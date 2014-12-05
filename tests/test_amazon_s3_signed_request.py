# -*- coding: utf-8 -*-
import base64
import json

import freezegun
import pytest
from flexmock import flexmock

from pontus import AmazonS3SignedRequest
from pontus._compat import force_text

HOUR_IN_SECONDS = 60 * 60


class TestAmazonS3SignedRequest(object):
    @pytest.fixture
    def signed_request(self, bucket):
        return AmazonS3SignedRequest(
            key_name='file_name.png',
            mime_type='image/png',
            bucket=bucket,
            acl='private',
            expires_in=HOUR_IN_SECONDS
        )

    def test_key(self, signed_request):
        assert signed_request.key_name == (
            'test-unvalidated-uploads/file_name.png'
        )

    def test_get_signature(self, signed_request):
        signature = signed_request._get_signature('some policy')
        assert signature == '+kyVfzakuUYOwB4mwo2CuG5GiGI='

    def test_get_policy_document(self, signed_request):
        with freezegun.freeze_time('2007-12-01 12:05:37.572123'):
            policy = signed_request._get_policy_document()
        data_as_json = base64.b64decode(policy)
        data = json.loads(force_text(data_as_json))
        assert data == {
            'expiration': '2007-12-01T13:05:37.572123Z',
            'conditions': [
                {'bucket': 'test-bucket'},
                {'key': 'test-unvalidated-uploads/file_name.png'},
                {'acl': 'private'},
                ['starts-with', '$Content-Type', ''],
                ['content-length-range', 0, 20971520],
                {'success_action_status': '201'},
            ]
        }

    def test_form_fields(self, signed_request):
        (
            flexmock(signed_request)
            .should_receive('_get_policy_document')
            .and_return(u'policy')
        )
        (
            flexmock(signed_request)
            .should_receive('_get_signature')
            .and_return(u'signature')
        )
        assert signed_request.form_fields == {
            'AWSAccessKeyId': 'test-key',
            'acl': 'private',
            'key': 'test-unvalidated-uploads/file_name.png',
            'Policy': 'policy',
            'success_action_status': '201',
            'Signature': 'signature',
        }

    def test_repr(self, signed_request):
        assert repr(signed_request) == (
            u"<AmazonS3SignedRequest " +
            u"key_name='test-unvalidated-uploads/file_name.png'>"
        )

    def test_randomized_key(self, bucket):
        import uuid
        (
            flexmock(uuid)
            .should_receive('uuid4')
            .and_return(u'random-string')
        )
        signed_request = AmazonS3SignedRequest(
            key_name='file_name.png',
            mime_type='image/png',
            randomize=True,
            bucket=bucket
        )
        assert signed_request.key_name == (
            'test-unvalidated-uploads/random-string/file_name.png'
        )
