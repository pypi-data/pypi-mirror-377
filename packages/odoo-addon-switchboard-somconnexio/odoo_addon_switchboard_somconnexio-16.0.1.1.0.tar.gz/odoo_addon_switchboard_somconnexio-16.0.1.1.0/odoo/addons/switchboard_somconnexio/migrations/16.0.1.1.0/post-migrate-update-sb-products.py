# Copyright 2025 Coopdevs Treball SCCL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
import logging

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    update_sb_product_custom_name(env)
    update_sb_product_product_tmpl_id(env)
    update_sb_external_provisioning_required(env)


def update_sb_product_custom_name(env):
    """
    The no-update value prevents to automatically update the changed
    custom names from some changed switchboard products.
    This migration makes sure the new custom names are saved in DB.
    """
    product_xml_ids_to_rename = [
        "AgentCentraletaVirtualApp500",
        "AgentCentraletaVirtualDesktop500",
        "AgentCentraletaVirtualAppUNL",
        "AgentCentraletaVirtualDesktopUNL",
        "AgentCentraletaVirtualBasic",
    ]
    for xml_id in product_xml_ids_to_rename:
        sb_product = env.ref(
            f"switchboard_somconnexio.{xml_id}", raise_if_not_found=False
        )
        if sb_product:
            sb_product.write({"custom_name": sb_product.custom_name})
            _logger.info(
                f"Updated SB Product Name for {xml_id} as {sb_product.custom_name}."
            )


def update_sb_product_product_tmpl_id(env):
    """
    This migration updates the product_template.id for specific switchboard products.
    """
    product_xml_ids_to_update = [
        "CentraletaVirtualSIMUNL10GB",
        "CentraletaVirtualSIMUNL20GB",
        "CentraletaVirtualSIMUNLUNL",
    ]
    for xml_id in product_xml_ids_to_update:
        sb_product = env.ref(
            f"switchboard_somconnexio.{xml_id}", raise_if_not_found=False
        )
        if sb_product:
            tmpl = sb_product.product_tmpl_id
            sb_product.write({"product_tmpl_id": tmpl})
            _logger.info(f"Updated SB Product Template ID for {xml_id} to {tmpl.name}.")


def update_sb_external_provisioning_required(env):
    """
    This migration sets external_provisioning_required to True
    for switchboard product templates.
    """

    product_tmpl_xml_ids_to_update = [
        "Switchboard_product_template",
        "Switchboard_mobile_product_template",
    ]

    for xml_id in product_tmpl_xml_ids_to_update:
        sb_template = env.ref(xml_id, raise_if_not_found=False)
        if not sb_template:
            _logger.warning(f"Could not find SB template for {xml_id}.")
            continue

        sb_template.write(
            {
                "external_provisioning_required": True,
            }
        )
        _logger.info(f"Set external_provisioning_required to True for {xml_id}.")
