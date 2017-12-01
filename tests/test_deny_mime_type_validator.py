# -*- coding: utf-8 -*-
import os

import pytest
import boto3

from pontus.exceptions import ValidationError
from pontus.validators import DenyMimeType


class TestDenyMimeTypeValidator(object):
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
        validator = DenyMimeType(mime_type='image/jpeg')
        with pytest.raises(ValidationError) as e:
            validator(jpeg_key)
        assert str(e.value) == (
            "Invalid file: File MIME type image/jpeg is in denied list "
            "image/jpeg."
        )

    def test_does_not_raise_validation_error_if_valid_mime_type(
        self,
        jpeg_key
    ):
        validator = DenyMimeType(mime_type='image/png')
        validator(jpeg_key)

    def test_repr(self):
        assert repr(DenyMimeType(mime_type='image/png')) == (
            u"<DenyMimeType mime_types='image/png'>"
        )

    def test_raises_validation_error_if_mime_type_not_in_valid_mime_types(
        self,
        jpeg_key
    ):
        validator = DenyMimeType(mime_types=['image/jpeg', 'application/csv'])
        with pytest.raises(ValidationError) as e:
            validator(jpeg_key)
        assert str(e.value) == (
            "Invalid file: File MIME type image/jpeg is in denied list "
            "['image/jpeg', 'application/csv']."
        )

    def test_doesnt_raise_validation_error_if_mime_type_in_valid_mime_types(
        self,
        jpeg_key
    ):
        validator = DenyMimeType(mime_types=['image/png', 'application/csv'])
        validator(jpeg_key)

    def test_raises_validation_error_if_mime_type_doesnt_match_regex(
        self,
        jpeg_key
    ):
        validator = DenyMimeType(regex=r'image\/.*')
        with pytest.raises(ValidationError) as e:
            validator(jpeg_key)
        assert str(e.value) == (
            "Invalid file: File MIME type image/jpeg matches denied regex "
            "r'image\/.*'."
        )

    def test_doesnt_raise_validation_error_if_mime_type_matches_regex(
        self,
        jpeg_key
    ):
        validator = DenyMimeType(regex=r'application\/.*')
        validator(jpeg_key)
