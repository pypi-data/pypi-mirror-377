"""
Tests for permissions part of the policy package
"""

import importlib

from rucio.common.types import InternalAccount


def test_import():
    importlib.import_module("bdms_rucio_policy.permission")


def test_has_permission():
    from bdms_rucio_policy.permission import has_permission

    account = InternalAccount("root")

    assert has_permission(account, "add_account", {}) is None
