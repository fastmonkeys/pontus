# -*- coding: utf-8 -*-
import os

import boto3
import pytest

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
            obj = boto3.resource('s3').Object(bucket.name, key_name)
            obj.put(
                Body=image
            )
            return obj

    def test_raises_validation_error_if_invalid_mime_type(
        self,
        jpeg_key
    ):
        validator = MimeType(mime_type='image/png')
        with pytest.raises(ValidationError) as e:
            validator(jpeg_key)
        assert str(e.value) == (
            "Invalid file: File MIME type is image/jpeg, not in image/png."
        )

    def test_does_not_raise_validation_error_if_valid_mime_type(
        self,
        jpeg_key
    ):
        validator = MimeType(mime_type='image/jpeg')
        validator(jpeg_key)

    def test_repr(self):
        assert repr(MimeType(mime_type='image/png')) == (
            u"<MimeType mime_types='image/png'>"
        )

    def test_raises_validation_error_if_mime_type_not_in_valid_mime_types(
        self,
        jpeg_key
    ):
        validator = MimeType(mime_types=['image/png', 'application/csv'])
        with pytest.raises(ValidationError) as e:
            validator(jpeg_key)
        assert str(e.value) == (
            "Invalid file: File MIME type is image/jpeg, not in "
            "['image/png', 'application/csv']."
        )

    def test_doesnt_raise_validation_error_if_mime_type_in_valid_mime_types(
        self,
        jpeg_key
    ):
        validator = MimeType(mime_types=['image/jpeg', 'application/csv'])
        validator(jpeg_key)

    def test_raises_validation_error_if_mime_type_doesnt_match_regex(
        self,
        jpeg_key
    ):
        validator = MimeType(regex=r'application\/.*')
        with pytest.raises(ValidationError) as e:
            validator(jpeg_key)
        assert str(e.value) == (
            "Invalid file: File MIME type image/jpeg does not match "
            "r'application\/.*'."
        )

    def test_doesnt_raise_validation_error_if_mime_type_matches_regex(
        self,
        jpeg_key
    ):
        validator = MimeType(regex=r'image\/.*')
        validator(jpeg_key)
