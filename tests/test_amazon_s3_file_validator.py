# -*- coding: utf-8 -*-
from flask.ext.storage import FileNotFoundError
from flexmock import flexmock
import pytest

from pontus import AmazonS3FileValidator
from pontus.exceptions import ValidationError
from pontus.validators import BaseValidator


HOUR_IN_SECONDS = 60 * 60


class CustomValidator(BaseValidator):
    def __call__(self, storage_file):
        if storage_file.name != 'test-unvalidated-uploads/images/hello.jpg':
            raise ValidationError('Invalid.')


class TestAmazonS3FileValidator(object):
    @pytest.fixture
    def amazon_s3_file_validator(self, mock_storage):
        key = 'test-unvalidated-uploads/images/hello.jpg'
        mock_storage.save(name=key, content='test')
        return AmazonS3FileValidator(
            key=key,
            storage=mock_storage,
            validators=[CustomValidator()]
        )

    @pytest.fixture
    def failing_amazon_s3_file_validator(self, mock_storage):
        key = 'images/fail.jpg'
        mock_storage.save(name=key, content='test')
        return AmazonS3FileValidator(
            key=key,
            storage=mock_storage,
            validators=[CustomValidator()]
        )

    def test_validate_calls_validators(self, amazon_s3_file_validator):
        (
            flexmock(CustomValidator)
            .should_receive('__call__')
            .with_args(amazon_s3_file_validator.file)
            .and_return(True)
        )
        amazon_s3_file_validator.validate()

    def test_validate_returns_true_when_validation_passes(
        self,
        amazon_s3_file_validator
    ):
        assert amazon_s3_file_validator.validate()

    def test_validator_has_no_errors_when_validation_passes(
        self,
        amazon_s3_file_validator
    ):
        assert not amazon_s3_file_validator.errors

    def test_validate_returns_false_when_validation_fails(
        self,
        failing_amazon_s3_file_validator
    ):
        assert not failing_amazon_s3_file_validator.validate()

    def test_validator_has_errors_when_validation_fails(
        self,
        failing_amazon_s3_file_validator
    ):
        failing_amazon_s3_file_validator.validate()
        assert failing_amazon_s3_file_validator.errors == ['Invalid.']

    def test_throws_error_if_file_not_found(
        self,
        mock_storage
    ):
        with pytest.raises(FileNotFoundError):
            AmazonS3FileValidator(
                key='does_not_exist.jpg',
                storage=mock_storage
            )

    def test_validate_removes_unvalidated_prefix_if_validation_passes(
        self,
        amazon_s3_file_validator,
        mock_storage
    ):
        amazon_s3_file_validator.validate()
        assert not mock_storage.exists(
            'test-unvalidated-uploads/images/hello.jpg'
        )
        assert mock_storage.exists('images/hello.jpg')
        assert not amazon_s3_file_validator.file.name.startswith(
            'test-unvalidated-uploads/'
        )
