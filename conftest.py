# -*- coding: utf-8 -*-
import boto
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
    conn = boto.connect_s3(
        aws_access_key_id='test-key',
        aws_secret_access_key='test-secret-key'
    )
    bucket = conn.create_bucket('test-bucket')
    return bucket


@pytest.yield_fixture(autouse=True)
def mock_amazon_s3():
    with mock_s3():
        yield
