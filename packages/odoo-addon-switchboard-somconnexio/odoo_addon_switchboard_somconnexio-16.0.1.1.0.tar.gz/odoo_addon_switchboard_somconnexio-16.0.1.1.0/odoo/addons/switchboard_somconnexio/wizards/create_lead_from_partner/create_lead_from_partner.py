from odoo import api, models


class CreateLeadFromPartnerWizard(models.TransientModel):
    _inherit = "partner.create.lead.wizard"

    def _create_isp_info_params(self):
        if self.product_categ_id != self.env.ref(
            "switchboard_somconnexio.switchboard_category"
        ):
            return super()._create_isp_info_params()

        isp_info_model_name = "switchboard.isp.info"
        isp_info_args = {
            "type": self.type,
            "phone_number": self.landline,
        }
        if self.type == "portability":
            isp_info_args.update(
                {
                    "previous_owner_vat_number": self.previous_owner_vat_number,
                    "previous_owner_name": self.previous_owner_name,
                    "previous_owner_first_name": self.previous_owner_first_name,
                }
            )

        isp_info_address_args = {
            "delivery_street": self.delivery_street,
            "delivery_zip_code": self.delivery_zip_code,
            "delivery_city": self.delivery_city,
            "delivery_state_id": self.delivery_state_id.id,
            "delivery_country_id": self.delivery_country_id.id,
            "invoice_street": self.invoice_street,
            "invoice_zip_code": self.invoice_zip_code,
            "invoice_city": self.invoice_city,
            "invoice_state_id": self.invoice_state_id.id,
            "invoice_country_id": self.invoice_country_id.id,
        }

        isp_info_res_id = self.env[isp_info_model_name].create(
            {**isp_info_args, **isp_info_address_args}
        )
        return isp_info_model_name, isp_info_res_id

    def _get_available_categories(self):
        available_categories = super()._get_available_categories()
        switchboard_category = self.env.ref(
            "switchboard_somconnexio.switchboard_category"
        )
        if (
            switchboard_category in available_categories
            and not self.partner_id.is_company
        ):
            return available_categories - switchboard_category
        else:
            return available_categories

    @api.depends("product_categ_id", "team_id")
    def _compute_available_products(self):
        if self.product_categ_id != self.env.ref(
            "switchboard_somconnexio.switchboard_category"
        ):
            return super()._compute_available_products()

        self.available_products = False
        available_product_templates = self._get_available_product_templates()
        attr_to_include = self.env.ref("somconnexio.Inclos")

        product_search_domain = [
            ("product_tmpl_id", "in", available_product_templates.ids),
            (
                "product_template_attribute_value_ids.product_attribute_value_id",
                "in",
                attr_to_include.ids,
            )
        ]

        self.available_products = self.env["product.product"].search(
            product_search_domain
        )
