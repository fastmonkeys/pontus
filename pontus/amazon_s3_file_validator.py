# -*- coding: utf-8 -*-
from flask import current_app
from flask.ext.storage import FileNotFoundError

from .exceptions import ValidationError


class AmazonS3FileValidator(object):
    def __init__(self, key, storage, validators=[]):
        self.errors = []
        self.file = storage.open(key)
        if not storage.exists(key):
            raise FileNotFoundError()
        self.key = key
        self.storage = storage
        self.validators = validators

    def validate(self):
        for validator in self.validators:
            try:
                validator(self.file)
            except ValidationError as e:
                self.errors.append(e.error)

        if not self.errors and self.has_unvalidated_prefix():
            self.move_to_validated()

        return len(self.errors) == 0

    def has_unvalidated_prefix(self):
        return (
            current_app.config.get('AWS_UNVALIDATED_PREFIX') and
            self.file.name.startswith(
                current_app.config.get('AWS_UNVALIDATED_PREFIX')
            )
        )

    def move_to_validated(self):
        new_name = self.file.name[
            len(current_app.config.get('AWS_UNVALIDATED_PREFIX')):
        ]
        new_file = self.storage.save(name=new_name, content=self.file.read())
        self.storage.delete(self.file.name)
        self.file = new_file
