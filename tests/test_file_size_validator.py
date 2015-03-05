# -*- coding: utf-8 -*-
import os

import pytest
from boto.s3.key import Key

from pontus.exceptions import ValidationError
from pontus.validators import FileSize


class TestFileSizeValidator(object):
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

    def test_raises_validation_error_if_file_is_too_large(
        self,
        jpeg_key
    ):
        validator = FileSize(max=27660)
        with pytest.raises(ValidationError) as e:
            validator(jpeg_key)
        assert e.value.error == (
            u'File is bigger than 27660 bytes.'
        )

    def test_raises_validation_error_if_file_is_too_small(
        self,
        jpeg_key
    ):
        validator = FileSize(min=27670)
        with pytest.raises(ValidationError) as e:
            validator(jpeg_key)
        assert e.value.error == (
            u'File is smaller than 27670 bytes.'
        )

    def test_does_not_raise_validation_error_if_file_is_of_valid_size(
        self,
        jpeg_key
    ):
        validator = FileSize(min=27660, max=27662)
        validator(jpeg_key)

    def test_raises_value_error_if_no_min_or_max_given(self):
        with pytest.raises(ValueError) as e:
            FileSize()
        assert str(e.value) == (
            'At least one of `min` or `max` must be defined.'
        )

    def test_raises_value_error_if_min_is_more_than_max(self):
        with pytest.raises(ValueError) as e:
            FileSize(min=2, max=1)
        assert str(e.value) == (
            'Argument `min` cannot be more than `max`.'
        )

    def test_repr(self):
        assert repr(FileSize(min=27660, max=27662)) == (
            u"<FileSize min=27660, max=27662>"
        )
