# -*- coding: utf-8 -*-
import pytest
from boto.s3.key import Key
from flexmock import flexmock

from pontus import AmazonS3FileValidator
from pontus.exceptions import FileNotFoundError, ValidationError
from pontus.validators import BaseValidator

HOUR_IN_SECONDS = 60 * 60


class CustomValidator(BaseValidator):
    def __call__(self, key):
        if key.name != 'test-unvalidated-uploads/images/hello.jpg':
            raise ValidationError('Invalid.')


class TestAmazonS3FileValidator(object):
    @pytest.fixture
    def amazon_s3_file_validator(self, bucket):
        key_name = 'test-unvalidated-uploads/images/hello.jpg'
        key = Key(bucket=bucket, name=key_name)
        key.set_contents_from_string('test')
        return AmazonS3FileValidator(
            key_name=key_name,
            bucket=bucket,
            validators=[CustomValidator()]
        )

    @pytest.fixture
    def failing_amazon_s3_file_validator(self, bucket):
        key_name = 'images/fail.jpg'
        key = Key(bucket=bucket, name=key_name)
        key.set_contents_from_string('test')
        return AmazonS3FileValidator(
            key_name=key,
            bucket=bucket,
            validators=[CustomValidator()]
        )

    def test_validate_calls_validators(self, amazon_s3_file_validator):
        (
            flexmock(CustomValidator)
            .should_receive('__call__')
            .with_args(amazon_s3_file_validator.key)
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
        bucket
    ):
        with pytest.raises(FileNotFoundError):
            AmazonS3FileValidator(
                key_name='does_not_exist.jpg',
                bucket=bucket
            )

    def test_validate_removes_unvalidated_prefix_if_validation_passes(
        self,
        amazon_s3_file_validator,
        bucket
    ):
        amazon_s3_file_validator.validate()
        assert bucket.get_key(
            'test-unvalidated-uploads/images/hello.jpg'
        ) is None
        assert bucket.get_key('images/hello.jpg')
        assert not amazon_s3_file_validator.key.name.startswith(
            'test-unvalidated-uploads/'
        )

    def test_repr(self, amazon_s3_file_validator):
        assert repr(amazon_s3_file_validator) == (
            "<AmazonS3FileValidator " +
            "key='test-unvalidated-uploads/images/hello.jpg'>"
        )
