Pontus
======

|Build Status|

Flask utility for signing Amazon S3 POST requests and validating Amazon S3
files. Both Python 2.7 and 3.4 are supported.

**Upgrade note: Pontus 1.x branch uses Boto3. If you are still using boto, use
0.x.x versions. Check Git branch `version-0`.**

Installation
------------

Install with pip::

    pip install Pontus


Dependencies
------------

Pontus has the following dependencies:

- Flask >= 0.10.1
- boto3 >= 1.4.7
- python-magic >= 0.4.6 (https://github.com/ahupp/python-magic)

Moreover python-magic depends on the libmagic file type identification library.


Examples
--------

Signed POST request
^^^^^^^^^^^^^^^^^^^

Creating form fields for a signed Amazon S3 POST request

.. code:: python

    import boto3
    from flask import current_app
    from pontus import AmazonS3SignedRequest

    session = boto3.session.Session(
        aws_access_key_id=current_app.config.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=current_app.config.get('AWS_SECRET_ACCESS_KEY'),
        region_name=current_app.config.get('AWS_REGION_NAME')
    )
    bucket = session.resource('s3').Bucket('testbucket')

    signed_request = AmazonS3SignedRequest(
        key_name=u'my/file.jpg',
        mime_type=u'image/jpeg',
        bucket=bucket,
        session=session
    )

    signed_request.form_fields

    # {
    #     'AWSAccessKeyId': 'your-aws-access-key-id',
    #     'success_action_status': '201',
    #     'acl': 'public-read',
    #     'Content-Type': 'image/png',
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

    import boto3
    from flask import current_app
    from pontus import AmazonS3FileValidator
    from pontus.validators import FileSize, MimeType

    session = boto3.session.Session(
        aws_access_key_id=current_app.config.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=current_app.config.get('AWS_SECRET_ACCESS_KEY')
    )
    bucket = session.resource('s3').Bucket('testbucket')

    validator = AmazonS3FileValidator(
        key_name='images/my-image.jpg',
        bucket=bucket,
        validators=[FileSize(max=2097152), MimeType('image/jpeg')],
        session=session
    )

    if validator.validate():
        # File is <2MB image/jpeg
        pass
    else:
        # File was invalid, printing errors
        print validator.errors


Validators can either be instances of a class inheriting
:code:`pontus.validators.BaseValidator` or callable functions that take one
parameter :code:`obj`, which is a `boto.S3.Object`_ instance.

.. code:: python

    from pontus.exceptions import ValidationError
    from pontus.validators import BaseValidator

    def name_starts_with_images(obj):
        if not obj.key.startswith('images/'):
            raise ValidationError()

    # OR

    class NameStartsWith(BaseValidator):
        def __init__(self, starts_with_str):
            self.starts_with_str = starts_with_str

        def __call__(self, obj):
            if not obj.key.startswith(starts_with_str):
                raise ValidationError()

    name_starts_with_images = NameStartsWith('images/')


.. _boto.S3.Object:
    http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Object

.. |Build Status| image:: https://circleci.com/gh/fastmonkeys/pontus.png?circle-token=d6d8af8b7529f93824baff06002e819764a77431
