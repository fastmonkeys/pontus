# -*- coding: utf-8 -*-
from .exceptions import MisconfiguredError


REQUIRED_STORAGE_ATTRS = [
    'access_key',
    'bucket_name',
    'acl',
    'secret_key'
]


def check_configuration_variables(storage):
    missing_attributes = []
    for attr in REQUIRED_STORAGE_ATTRS:
        if not (hasattr(storage, attr) and getattr(storage, attr)):
            missing_attributes.append(attr)

    if missing_attributes:
        raise MisconfiguredError(attrs=missing_attributes)
