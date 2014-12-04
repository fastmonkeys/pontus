Pontus
======

|Build Status|

Flask utility for signing Amazon S3 POST requests and validating Amazon S3
files. Both Python 2.7 and 3.4 are supported.


Installation
------------

Install with pip::

    pip install Pontus


Dependencies
------------

Pontus has the following dependencies:

- Flask >= 0.10.1
- boto >= 2.34.0
- python-magic >= 0.4.6 (https://github.com/ahupp/python-magic)

Moreover python-magic depends on the libmagic file type identification library.


Examples
--------

Signed POST request
^^^^^^^^^^^^^^^^^^^

Creating form fields for a signed Amazon S3 POST request

.. code:: python

    import boto
    from flask import current_app
    from pontus import AmazonS3SignedRequest

    connection = boto.s3.connection.S3Connection(
        aws_access_key_id=current_app.config.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=current_app.config.get('AWS_SECRET_ACCESS_KEY')
    )
    bucket = connection.get_bucket('testbucket')

    signed_request = AmazonS3SignedRequest(
        key_name=u'my/file.jpg',
        mime_type=u'image/jpeg',
        bucket=bucket,
    )

    signed_request.form_fields

    # {
    #     'AWSAccessKeyId': 'your-aws-access-key-id',
    #     'success_action_status': '201',
    #     'acl': 'public-read',
    #     'key': u'f6c157e1-1a1a-4418-99fe-3362dcf7b1ea/images/my-image.jpg',
    #     'Signature': 'generated-signature',
    #     'Policy': 'generated-policy-document'
    # }


These form fields can be used to POST files to Amazon S3 as described in
`Amazon's documentation`_.

.. _Amazon's documentation:
   http://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-authentication-HTTPPOST.html


Amazon S3 file validation
^^^^^^^^^^^^^^^^^^^^^^^^^

Validating that an image file is less than 2MB and is of :code:`image/jpeg`
MIME type.

.. code:: python

    import boto
    from flask import current_app
    from pontus import AmazonS3FileValidator
    from pontus.validators import FileSize, MimeType

    connection = boto.s3.connection.S3Connection(
        aws_access_key_id=current_app.config.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=current_app.config.get('AWS_SECRET_ACCESS_KEY')
    )
    bucket = connection.get_bucket('testbucket')

    validator = AmazonS3FileValidator(
        key_name='images/my-image.jpg',
        bucket=bucket,
        validators=[FileSize(max=2097152), MimeType('image/jpeg')]
    )

    if validator.validate():
        # File is <2MB image/jpeg
        pass
    else:
        # File was invalid, printing errors
        print validator.errors


Validators can either be instances of a class inheriting
:code:`pontus.validators.BaseValidator` or callable functions that take one
parameter :code:`key`, which is a `boto.s3.key.Key`_ instance.

.. code:: python

    from pontus.exceptions import ValidationError
    from pontus.validators import BaseValidator

    def name_starts_with_images(key):
        if not key.name.startswith('images/'):
            raise ValidationError()

    # OR

    class NameStartsWith(BaseValidator):
        def __init__(self, starts_with_str):
            self.starts_with_str = starts_with_str

        def __call__(self, key):
            if not key.name.startswith(starts_with_str):
                raise ValidationError()

    name_starts_with_images = NameStartsWith('images/')


.. _boto.s3.key.Key:
    http://boto.readthedocs.org/en/latest/ref/s3.html#module-boto.s3.key

.. |Build Status| image:: https://circleci.com/gh/fastmonkeys/pontus.png?circle-token=d6d8af8b7529f93824baff06002e819764a77431
