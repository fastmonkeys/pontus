Changelog
---------

3.0.0 (June 3rd, 2019)
^^^^^^^^^^^^^^^^^^^^^^^^

- Update AmazonS3SignedRequest to use AWS Signature Version 4 instead of Version 2. BREAKING CHANGE: Session object must have region_name defined.


2.2.0 (January 29th, 2019)
^^^^^^^^^^^^^^^^^^^^^^^^

- Add new_file_acl argument to AmazonS3FileValidator.


2.1.0 (November 5th, 2018)
^^^^^^^^^^^^^^^^^^^^^^^^

- Add new_file_prefix argument to AmazonS3FileValidator.
- Add delete_unvalidated_file armgument to AmazonS3FileValidator.


2.0.1 (July 26th, 2018)
^^^^^^^^^^^^^^^^^^^^^^^^

- Use universal wheel.
- Include license in wheel.


2.0.0 (July 11th, 2018)
^^^^^^^^^^^^^^^^^^^^^^^^

- Add Content-Type validation to AmazonS3SignedRequest.

1.0.0 (December 5th, 2017)
^^^^^^^^^^^^^^^^^^^^^^^^

- Switch to boto3.
- Drop support for boto.

0.2.1 (March 5th, 2015)
^^^^^^^^^^^^^^^^^^^^^^^^

- Fix hanging tests.
- Add support for multiple MIME types and regex patterns to MimeType validator.
- Add DenyMimeType validator.

0.2.0 (December 5th, 2014)
^^^^^^^^^^^^^^^^^^^^^^^^

- Replace Flask-Storage dependency with boto.
- Add support for Python 3.

0.1.0 (July 9th, 2014)
^^^^^^^^^^^^^^^^^^^^^^^^

- Initial release.
