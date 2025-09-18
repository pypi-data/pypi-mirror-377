from odoo import models, fields, api, _


class CrmLeadAddSBLineWizard(models.TransientModel):
    _name = "crm.lead.add.sb.line.wizard"
    _description = "Wizard per afegir línies de centraleta virtual"

    lead_id = fields.Many2one("crm.lead", string="CRM Lead", required=True)
    agent_line_ids = fields.Many2many("agent.sb", string="SB Agents")
    landline_line_ids = fields.Many2many("landline.sb", string="SB Landlines")

    def action_new_agent(self):
        """Open pop-up to add new agent"""
        return {
            "name": _("Add Agent"),
            "type": "ir.actions.act_window",
            "res_model": "agent.sb",
            "view_mode": "form",
            "view_id": self.env.ref("switchboard_somconnexio.view_agent_sb_form").id,
            "target": "new",
        }

    def action_new_landline(self):
        """Open pop-up to add new landline"""
        return {
            "name": _("Add Landline"),
            "type": "ir.actions.act_window",
            "res_model": "landline.sb",
            "view_mode": "form",
            "view_id": self.env.ref("switchboard_somconnexio.view_landline_sb_form").id,
            "target": "new",
        }

    def _open_wizard(self):
        """Open the wizard"""
        return {
            "type": "ir.actions.act_window",
            "name": _("Switchboard Virtual Constructor"),
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "view_id": self.env.ref(
                "switchboard_somconnexio.view_crm_lead_add_sb_line_wizard_form"
            ).id,
            "target": "new",
        }

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults["lead_id"] = self.env.context.get("active_id")
        return defaults

    def button_add(self):
        """Adds the SB lines to the CRM lead"""
        for agent_line in self.agent_line_ids:
            agent_line._create_lead_line()
        for landline_line in self.landline_line_ids:
            landline_line._create_lead_line()

        return True

    def button_cancel(self):
        """Close the wizard without saving"""
        for agent_line in self.agent_line_ids:
            agent_line.unlink()
        for landline_line in self.landline_line_ids:
            landline_line.unlink()
        return {
            "type": "ir.actions.act_window_close",
        }


class AgentSwitchboard(models.TransientModel):
    _name = "agent.sb"
    _description = "SB Agent to add to CRM Lead"

    wizard_id = fields.Many2one("crm.lead.add.sb.line.wizard", required=True)
    bank_id = fields.Many2one(
        "res.partner.bank",
        string="Bank Account",
        domain="[('partner_id', '=', partner_id)]",
        required=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
    )
    agent_name = fields.Char("Agent name", required=True)
    agent_email = fields.Char("Agent email")
    extension = fields.Char("Extension", required=True)
    product_id = fields.Many2one(
        "product.product",
        string="Main product SB",
        required=True,
        domain=lambda self: self._main_product_domain(),
    )
    mobile_product_id = fields.Many2one(
        "product.product",
        string="Mobile product SB",
        domain=lambda self: self._mobile_product_domain(),
    )
    icc = fields.Char(string="ICC")
    integration_product_id = fields.Many2one(
        "product.product",
        string="Integration product SB",
        domain=lambda self: self._integration_product_domain(),
    )
    device_product_id = fields.Many2one(
        "product.product",
        string="Device product SB",
        domain=lambda self: self._device_product_domain(),
    )
    provision_type = fields.Selection(
        [("portability", "Portability"), ("new", "New")],
        string="Type",
    )
    phone_number = fields.Char(
        string="Phone Number",
    )
    previous_owner_first_name = fields.Char(
        string="Previous owner first name",
    )
    previous_owner_name = fields.Char(
        string="Previous owner name",
    )
    previous_owner_vat_number = fields.Char(
        string="Previous owner VAT number",
    )

    def _mobile_product_domain(self):
        """Domain for the mobile product selection"""
        mobile_sb_template = self.env.ref(
            "switchboard_somconnexio.Switchboard_mobile_product_template",
        )
        return [
            ("product_tmpl_id", "=", mobile_sb_template.id),
        ]

    def _integration_product_domain(self):
        """Domain for the team product selection"""
        integration_sb_template = self.env.ref(
            "switchboard_somconnexio.Switchboard_integration_product_template",
        )
        return [
            ("product_tmpl_id", "=", integration_sb_template.id),
        ]

    def _device_product_domain(self):
        """Domain for the device product selection"""
        device_sb_template = self.env.ref(
            "switchboard_somconnexio.Switchboard_device_product_template",
        )
        return [
            ("product_tmpl_id", "=", device_sb_template.id),
        ]

    @api.model
    def default_get(self, fields_list):
        """Set wizard_id value"""
        defaults = super().default_get(fields_list)
        wizard_id = self.env.context.get("active_id")
        wizard = self.env["crm.lead.add.sb.line.wizard"].browse(wizard_id)
        defaults["wizard_id"] = wizard.id
        lead = self.env["crm.lead"].browse(wizard.lead_id.id)
        defaults["partner_id"] = lead.partner_id.id
        return defaults

    def action_save_agent(self):
        """Save agent and close pop-up"""
        self.wizard_id.agent_line_ids = [(4, self.id)]

        return self.wizard_id._open_wizard()

    def action_go_back(self):
        """Go back and close pop-up"""
        return self.wizard_id._open_wizard()

    def action_remove_agent(self):
        """Remove agent and close pop-up"""
        self.wizard_id.agent_line_ids = [(3, self.id)]

        return self.wizard_id._open_wizard()

    def action_edit_agent(self):
        """Open pop-up to edit this agent"""
        return {
            "name": _("Edit Agent"),
            "type": "ir.actions.act_window",
            "res_model": "agent.sb",
            "res_id": self.id,
            "view_mode": "form",
            "view_id": self.env.ref("switchboard_somconnexio.view_agent_sb_form").id,
            "target": "new",
        }

    def _main_product_domain(self):
        """Domain for the main switchboard product selection"""
        main_sb_template = self.env.ref(
            "switchboard_somconnexio.Switchboard_product_template",
        )
        fix_product = self.env.ref(
            "switchboard_somconnexio.FixCentraletaVirtual",
        )
        return [
            ("product_tmpl_id", "=", main_sb_template.id),
            ("id", "!=", fix_product.id),
        ]

    def _add_product_domain(self):
        """Domain for additional switchboard products"""
        return [("id", "in", self.available_add_products.ids)]

    def _create_lead_line(self):
        """Create a lead line for this agent"""
        CrmLeadLine = self.env["crm.lead.line"]
        SbIspInfo = self.env["switchboard.isp.info"]

        additional_product_ids = (
            self.mobile_product_id
            + self.integration_product_id
            + self.device_product_id
        )
        isp_info = SbIspInfo.create(
            {
                "mobile_phone_number": self.phone_number,
                "agent_name": self.agent_name,
                "agent_email": self.agent_email,
                "extension": self.extension,
                "additional_product_ids": additional_product_ids.ids,
                "icc": self.icc,
                "type": self.provision_type,
                "previous_owner_first_name": self.previous_owner_first_name,
                "previous_owner_name": self.previous_owner_name,
                "previous_owner_vat_number": self.previous_owner_vat_number,
            }
        )
        lead_line = CrmLeadLine.create(
            {
                "name": self.product_id.name,
                "product_id": self.product_id.id,
                "switchboard_isp_info": isp_info.id,
                "iban": self.bank_id.sanitized_acc_number,
            }
        )
        self.wizard_id.lead_id.write({"lead_line_ids": [(4, lead_line.id, 0)]})


class LandlineSwitchboard(models.TransientModel):
    _name = "landline.sb"
    _description = "Extra landline to add to CRM Lead"

    wizard_id = fields.Many2one("crm.lead.add.sb.line.wizard", required=True)
    bank_id = fields.Many2one(
        "res.partner.bank",
        string="Bank Account",
        domain="[('partner_id', '=', partner_id)]",
        required=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
    )
    phone_number = fields.Char(string="Phone Number", required=True)
    provision_type = fields.Selection(
        [("portability", "Portability"), ("new", "New")],
        string="Type",
    )
    previous_owner_first_name = fields.Char(
        string="Previous owner first name",
    )
    previous_owner_name = fields.Char(
        string="Previous owner name",
    )
    previous_owner_vat_number = fields.Char(
        string="Previous owner VAT number",
    )
    product_id = fields.Many2one(
        "product.product",
        string="Landline product",
        readonly=True,
        default=lambda self: self.env.ref(
            "switchboard_somconnexio.FixCentraletaVirtual", raise_if_not_found=False
        ),
    )
    call_product_id = fields.Many2one(
        "product.product",
        string="Call product SB",
        domain=lambda self: self._call_product_domain(),
    )

    @api.model
    def default_get(self, fields_list):
        """Set wizard_id value"""
        defaults = super().default_get(fields_list)
        wizard_id = self.env.context.get("active_id")
        wizard = self.env["crm.lead.add.sb.line.wizard"].browse(wizard_id)
        defaults["wizard_id"] = wizard.id
        lead = self.env["crm.lead"].browse(wizard.lead_id.id)
        defaults["partner_id"] = lead.partner_id.id
        return defaults

    def action_save_landline(self):
        """Save landline and close pop-up"""
        self.wizard_id.landline_line_ids = [(4, self.id)]

        return self.wizard_id._open_wizard()

    def action_go_back(self):
        """Go back and close pop-up"""
        return self.wizard_id._open_wizard()

    def action_remove_landline(self):
        """Remove landline and close pop-up"""
        self.wizard_id.landline_line_ids = [(3, self.id)]

        return self.wizard_id._open_wizard()

    def action_edit_landline(self):
        """Open pop-up to edit this landline"""
        return {
            "name": _("Edit Landline"),
            "type": "ir.actions.act_window",
            "res_model": "landline.sb",
            "res_id": self.id,
            "view_mode": "form",
            "view_id": self.env.ref("switchboard_somconnexio.view_landline_sb_form").id,
            "target": "new",
        }

    def _call_product_domain(self):
        """Domain for the call product selection"""
        call_sb_template = self.env.ref(
            "switchboard_somconnexio.Switchboard_call_product_template",
        )
        return [
            ("product_tmpl_id", "=", call_sb_template.id),
        ]

    def _create_lead_line(self):
        """Create a lead line for a landline"""
        CrmLeadLine = self.env["crm.lead.line"]
        SbIspInfo = self.env["switchboard.isp.info"]

        isp_info = SbIspInfo.create(
            {
                "phone_number": self.phone_number,
                "type": self.provision_type,
                "previous_owner_first_name": self.previous_owner_first_name,
                "previous_owner_name": self.previous_owner_name,
                "previous_owner_vat_number": self.previous_owner_vat_number,
            }
        )
        if self.call_product_id:
            isp_info.additional_product_ids = [(4, self.call_product_id.id, 0)]

        lead_line = CrmLeadLine.create(
            {
                "name": self.product_id.name,
                "product_id": self.product_id.id,
                "switchboard_isp_info": isp_info.id,
                "iban": self.bank_id.sanitized_acc_number,
            }
        )
        self.wizard_id.lead_id.write({"lead_line_ids": [(4, lead_line.id, 0)]})
