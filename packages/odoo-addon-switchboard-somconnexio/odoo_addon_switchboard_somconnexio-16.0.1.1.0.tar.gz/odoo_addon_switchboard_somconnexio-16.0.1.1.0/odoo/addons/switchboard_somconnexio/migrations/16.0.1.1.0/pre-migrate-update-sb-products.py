from openupgradelib import openupgrade
import logging

_logger = logging.getLogger(__name__)

_xml_ids_renames = [
    (
        "switchboard_somconnexio.CentraletaVirtualSIMBasic",
        "switchboard_somconnexio.AgentCentraletaVirtualBasic",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xml_ids_renames)

    _logger.info("Renamed XML IDs")
