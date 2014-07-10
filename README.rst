Pontus
======

Flask-Storage utils for:

- signing Amazon S3 POST requests
- validating Amazon S3 files


Installation
------------

Install with pip::

    pip install Pontus


Dependencies
------------

Pontus has the following dependencies:

- Flask >= 0.10.1
- Flask-Storage >= 0.1.3dev (https://github.com/kvesteri/flask-storage)
- python-magic >= 0.4.6 (https://github.com/ahupp/python-magic)

Moreover python-magic depends on the libmagic file type identification library.


Examples
--------

Signed POST request
^^^^^^^^^^^^^^^^^^^

Creating form fields for a signed Amazon S3 POST request::


    from pontus import AmazonS3SignedRequest

    signed_request = AmazonS3SignedRequest(
        key='images/my-image.jpg',
        mime_type='image/jpeg',
        storage=storage,
        randomize=True
    )

    signed_request.form_fields

    # {
    #     'AWSAccessKeyId': 'your-aws-access-key-id',
    #     'success_action_status': '201',
    #     'acl': 'private',
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
MIME type::

    from pontus import AmazonS3FileValidator
    from pontus.validators import FileSize, MimeType

    validator = AmazonS3FileValidator(
        key='images/my-image.jpg',
        storage=storage,
        validators=[FileSize(max=2097152), MimeType('image/jpeg')]
    )

    if validator.validate():
        # File is <2MB image/jpeg
        pass
    else:
        # File was invalid, printing errors
        print validator.errors


Validators can either be instances of a class inheriting
:code:`pontus.validators.BaseValidator` or callable functions that take
:code:`storage_file` as a parameter::

    from pontus.exceptions import ValidationError
    from pontus.validators import BaseValidator

    def name_starts_with_images(storage_file):
        if not storage_file.name.startswith('images/'):
            raise ValidationError()

    # OR

    class NameStartsWith(BaseValidator):
        def __init__(self, starts_with_str):
            self.starts_with_str = starts_with_str

        def __call__(self, storage_file):
            if not storage_file.name.startswith(starts_with_str):
                raise ValidationError()

    name_starts_with_images = NameStartsWith('images/')
