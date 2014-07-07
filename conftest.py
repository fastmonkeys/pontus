# -*- coding: utf-8 -*-
import pytest

from flask import Flask
from flask.ext.storage import MockStorage


@pytest.yield_fixture(scope='session', autouse=True)
def app(request):
    app = Flask('test')
    app.config.update(
        DEFAULT_FILE_STORAGE='amazon',
        AWS_ACCESS_KEY_ID='test-aws-access-key-id',
        AWS_SECRET_ACCESS_KEY='test-secret-access-key',
        AWS_STORAGE_BUCKET_NAME='test-bucket',
        AWS_UNVALIDATED_PREFIX='test-unvalidated-uploads/',
        AWS_DEFAULT_ACL='private'
    )
    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()


@pytest.yield_fixture
def mock_storage():
    storage = MockStorage()
    yield storage
    storage._files = {}
