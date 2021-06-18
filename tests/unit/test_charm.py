# Copyright 2021 Joseph Borg <joseph.borg@canonical.com>
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

import pytest
from ops.model import ActiveStatus, BlockedStatus
from ops.testing import Harness
from charm import CoderOperator


@pytest.fixture
def harness():
    harness = Harness(CoderOperator)
    try:
        yield harness
    finally:
        harness.cleanup()


def test_valid_config(harness):
    harness.begin()
    harness.update_config({"password": "foo"})
    assert isinstance(harness.charm.unit.status, ActiveStatus)


def test_invalid_config(harness):
    harness.begin()
    harness.update_config({"password": ""})
    assert isinstance(harness.charm.unit.status, BlockedStatus)


def test_register_ingress(harness):
    harness.set_leader(True)
    harness.begin()
    rid = harness.add_relation("ingress", "ingress")
    rel = harness.model.get_relation("ingress", rid)
    harness.add_relation_unit(rid, "ingress/0")
    assert rel.data[harness.charm.app] == {
        "service-hostname": "coder.juju",
        "service-name": "coder",
        "service-port": 8080,
    }
