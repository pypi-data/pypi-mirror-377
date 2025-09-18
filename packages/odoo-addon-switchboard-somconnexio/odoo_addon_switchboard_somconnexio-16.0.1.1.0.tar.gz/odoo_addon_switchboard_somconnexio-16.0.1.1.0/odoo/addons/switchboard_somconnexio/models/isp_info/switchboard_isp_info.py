from odoo import models, fields, api


class SwitchboardISPInfo(models.Model):
    _name = "switchboard.isp.info"
    _inherit = "base.isp.info"
    _description = "Switchboard ISP Info"

    phone_number = fields.Char("Landline phone number", required=False)
    phone_number_2 = fields.Char(
        "Second landline phone number"
    )  # Deprecated field, kept for compatibility
    mobile_phone_number = fields.Char("Mobile phone number")
    agent_name = fields.Char("Agent name")
    agent_email = fields.Char("Agent email")
    extension = fields.Char("Extension")
    icc = fields.Char("ICC")
    has_sim = fields.Boolean(string="Has sim card", default=False)
    additional_product_ids = fields.Many2many(
        "product.product",
        string="Additional products",
        domain=lambda self: self._additional_product_domain(),
    )
    has_mobile = fields.Boolean(
        compute="_compute_has_mobile",
        default=False,
    )

    def _compute_has_mobile(self):
        mobile_sb_template = self.env.ref(
            "switchboard_somconnexio.Switchboard_mobile_product_template"
        )
        for record in self:
            if not record.additional_product_ids:
                record.has_mobile = False
            record.has_mobile = any(
                p.product_tmpl_id == mobile_sb_template
                for p in record.additional_product_ids
            )

    def _additional_product_domain(self):
        """Compute the available additional products for the ISP info"""
        sb_add_category = self.env.ref(
            "switchboard_somconnexio.switchboard_additional_service",
            raise_if_not_found=False,
        )
        if not sb_add_category:
            return []
        sb_add_categories = self.env["product.category"].search(
            [("id", "child_of", sb_add_category.id)]
        )
        product_tmpl_ids = self.env["product.template"].search(
            [
                ("categ_id", "in", sb_add_categories.ids),
            ]
        )
        return [
            ("product_tmpl_id", "in", product_tmpl_ids.ids),
        ]

    @api.constrains("type", "previous_provider")
    def _check_portability_info(self):
        """
        TODO: Switchboard portabilities do not need
        previous providers so far.
        If eventually they do, remove this
        """
        return True
