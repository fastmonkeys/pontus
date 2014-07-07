# -*- coding: utf-8 -*-
import os

import pytest

from pontus.exceptions import ValidationError
from pontus.validators import FileSize, MimeType


class TestMimeTypeValidator(object):
    @pytest.fixture
    def jpeg_storage_file(self, mock_storage):
        with open(os.path.join(
            os.path.dirname(__file__),
            'data',
            'example.jpg'
        ), 'rb') as image:
            return mock_storage.save(
                name=u'example.jpg',
                content=image.read()
            )

    def test_raises_validation_error_if_invalid_mime_type(
        self,
        jpeg_storage_file
    ):
        validator = MimeType(mime_type='image/png')
        with pytest.raises(ValidationError) as e:
            validator(jpeg_storage_file)
        assert e.value.error == (
            u"File MIME type is 'image/jpeg', not 'image/png'."
        )

    def test_does_not_raise_validation_error_if_valid_mime_type(
        self,
        jpeg_storage_file
    ):
        validator = MimeType(mime_type='image/jpeg')
        validator(jpeg_storage_file)


class TestFileSizeValidator(object):
    @pytest.fixture
    def jpeg_storage_file(self, mock_storage):
        with open(os.path.join(
            os.path.dirname(__file__),
            'data',
            'example.jpg'
        ), 'rb') as image:
            return mock_storage.save(
                name=u'example.jpg',
                content=image.read()
            )

    def test_raises_validation_error_if_file_is_too_large(
        self,
        jpeg_storage_file
    ):
        validator = FileSize(max=27660)
        with pytest.raises(ValidationError) as e:
            validator(jpeg_storage_file)
        assert e.value.error == (
            u'File is bigger than 27660 bytes.'
        )

    def test_raises_validation_error_if_file_is_too_small(
        self,
        jpeg_storage_file
    ):
        validator = FileSize(min=27670)
        with pytest.raises(ValidationError) as e:
            validator(jpeg_storage_file)
        assert e.value.error == (
            u'File is smaller than 27670 bytes.'
        )

    def test_does_not_raise_validation_error_if_file_is_of_valid_size(
        self,
        jpeg_storage_file
    ):
        validator = FileSize(min=27660, max=27662)
        validator(jpeg_storage_file)

    def test_raises_value_error_if_no_min_or_max_given(self):
        with pytest.raises(ValueError) as e:
            FileSize()
        assert e.value.message == (
            u'At least one of `min` or `max` must be defined.'
        )

    def test_raises_value_error_if_min_is_more_than_max(self):
        with pytest.raises(ValueError) as e:
            FileSize(min=2, max=1)
        assert e.value.message == (
            u'Argument `min` cannot be more than `max`.'
        )
