# -*- coding: utf-8 -*-
from flask import current_app
from flask.ext.storage import get_default_storage_class
import pytest

from pontus.exceptions import MisconfiguredError
from pontus.utils import check_configuration_variables, REQUIRED_STORAGE_ATTRS


class TestCheckConfigurationVariables(object):
    @pytest.fixture
    def storage(self):
        return get_default_storage_class(current_app)()

    def test_does_not_raise_error_if_all_configs_found(self, storage):
        check_configuration_variables(storage)

    @pytest.mark.parametrize('attr', REQUIRED_STORAGE_ATTRS)
    def test_raises_misconfigured_error_if_configs_missing(
        self,
        storage,
        attr
    ):
        setattr(storage, attr, None)
        with pytest.raises(MisconfiguredError):
            check_configuration_variables(storage)

    def test_lists_only_attributes_that_are_missing(self, storage):
        setattr(storage, REQUIRED_STORAGE_ATTRS[0], None)
        setattr(storage, REQUIRED_STORAGE_ATTRS[1], None)
        with pytest.raises(MisconfiguredError) as e:
            check_configuration_variables(storage)
        assert str(e.value) == (
            'Flask-Storage instance missing attributes for AWS. ' +
            'Missing attributes: %s.'
        ) % (', '.join(REQUIRED_STORAGE_ATTRS[:2]))
