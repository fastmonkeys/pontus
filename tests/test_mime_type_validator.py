# -*- coding: utf-8 -*-
import os

import pytest
from boto.s3.key import Key

from pontus.exceptions import ValidationError
from pontus.validators import MimeType


class TestMimeTypeValidator(object):
    @pytest.fixture
    def jpeg_key(self, bucket):
        with open(os.path.join(
            os.path.dirname(__file__),
            'data',
            'example.jpg'
        ), 'rb') as image:
            key_name = 'example.jpg'
            key = Key(bucket=bucket, name=key_name)
            key.set_contents_from_file(image)
            return key

    def test_raises_validation_error_if_invalid_mime_type(
        self,
        jpeg_key
    ):
        validator = MimeType(mime_type='image/png')
        with pytest.raises(ValidationError) as e:
            validator(jpeg_key)
        assert str(e.value) == (
            "Invalid file: File MIME type is image/jpeg, not image/png."
        )

    def test_does_not_raise_validation_error_if_valid_mime_type(
        self,
        jpeg_key
    ):
        validator = MimeType(mime_type='image/jpeg')
        validator(jpeg_key)

    def test_repr(self):
        assert repr(MimeType(mime_type='image/png')) == (
            u"<MimeType mime_type='image/png'>"
        )
