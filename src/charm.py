#!/usr/bin/env python3
# Copyright 2021 Joseph Borg <joseph.borg@canonical.com>
# See LICENSE file for licensing details.

import logging

from charms.nginx_ingress_integrator.v0.ingress import IngressRequires

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus, ModelError

logger = logging.getLogger(__name__)


class CoderCharm(CharmBase):
    """
    Charm the service.
    """

    _stored = StoredState()

    def __init__(self, *args):
        """
        Set up observations and ingress.
        """
        super().__init__(*args)
        self.framework.observe(self.on.coder_pebble_ready, self._on_coder_pebble_ready)
        self.framework.observe(self.on.config_changed, self._on_config_changed)

        self.ingress = IngressRequires(
            self,
            {
                "service-hostname": self._external_hostname,
                "service-name": self.app.name,
                "service-port": 8080,
            },
        )

    @property
    def _external_hostname(self):
        """
        Check if hostname has been configured. If not, generate one.
        """
        return self.config["external-hostname"] or "{}.juju".format(self.app.name)

    def _on_coder_pebble_ready(self, event):
        """
        Start the Coder server.
        """
        if not self.model.config.get("password"):
            self.unit.status = BlockedStatus("You must set a password")
            event.defer()
            return

        container = event.workload
        pebble_layer = {
            "summary": "coder layer",
            "description": "pebble config layer for coder",
            "services": {
                "coder": {
                    "override": "replace",
                    "summary": "coder",
                    "command": "code-server --bind-addr 0.0.0.0:8080",
                    "startup": "enabled",
                    "environment": {"PASSWORD": self.model.config.get("password")},
                }
            },
        }
        container.add_layer("coder", pebble_layer, combine=True)
        container.autostart()
        self.unit.status = ActiveStatus()

    def _on_config_changed(self, event):
        """
        Update the layer with new config.
        """
        if not self.model.config.get("password"):
            self.unit.status = BlockedStatus("You must set a password")
            return

        container = self.unit.get_container("coder")
        plan = container.get_plan()

        try:
            service = container.get_service("pause")
        except ConnectionError:
            logger.info("Pebble API not yet ready, waiting...")
            event.defer()
            return
        except ModelError:
            logger.info("Service 'coder' not yet defined, waiting...")
            event.defer()
            return

        patch_layer = {
            "services": {
                "coder": {
                    "override": "merge",
                    "environment": {"PASSWORD": self.model.config.get("password")},
                }
            }
        }

        if plan.services["environment"] != patch_layer["services"]["environment"]:
            try:
                container.add_layer("pause", patch_layer, combine=True)
            except ConnectionError:
                logger.info("Pebble API not yet ready, waiting...")
                event.defer()
                return

            if service.is_running():
                container.stop("pause")
                container.start("pause")

        self.unit.status = ActiveStatus()


if __name__ == "__main__":
    main(CoderCharm)
