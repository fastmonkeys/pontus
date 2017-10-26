# -*- coding: utf-8 -*-
import boto3
import pytest
from flask import Flask
from moto import mock_s3


@pytest.yield_fixture(scope='session', autouse=True)
def app(request):
    app = Flask('test')
    app.config.update(AWS_UNVALIDATED_PREFIX='test-unvalidated-uploads/')
    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()


@pytest.fixture
def bucket(request):
    boto3.resource('s3').create_bucket(Bucket='test-bucket')
    return boto3.resource('s3').Bucket('test-bucket')


@pytest.yield_fixture(autouse=True)
def mock_amazon_s3():
    with mock_s3():
        yield
