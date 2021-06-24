# Copyright 2021 Joseph Borg <joseph.borg@canonical.com>
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

import logging
import pytest

log = logging.getLogger(__name__)


@pytest.mark.abort_on_fail
async def test_build_and_deploy(ops_test):
    charm = await ops_test.build_charm(".")
    await ops_test.model.deploy(charm, config={"password": "foo"})
    await ops_test.model.deploy("nginx-ingress-integrator")
    await ops_test.model.add_relation("coder", "nginx-ingress-integrator")
    await ops_test.model.wait_for_idle(wait_for_active=True)
