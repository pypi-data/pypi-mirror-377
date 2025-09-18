from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CRMLeadLine(models.Model):
    _inherit = "crm.lead.line"

    switchboard_isp_info = fields.Many2one(
        "switchboard.isp.info", string="Switchboard ISP Info"
    )
    is_switchboard = fields.Boolean(
        compute="_compute_is_switchboard",
        store=True,
    )

    switchboard_isp_info_icc = fields.Char(
        related="switchboard_isp_info.icc", store=True
    )
    switchboard_isp_info_type = fields.Selection(related="switchboard_isp_info.type")
    switchboard_isp_info_phone_number = fields.Char(
        related="switchboard_isp_info.phone_number"
    )
    switchboard_isp_info_mobile_phone_number = fields.Char(
        related="switchboard_isp_info.mobile_phone_number"
    )
    switchboard_isp_info_agent_name = fields.Char(
        related="switchboard_isp_info.agent_name"
    )
    switchboard_isp_info_agent_email = fields.Char(
        related="switchboard_isp_info.agent_email"
    )
    switchboard_isp_info_extension = fields.Char(
        related="switchboard_isp_info.extension"
    )
    switchboard_isp_info_invoice_street = fields.Char(
        related="switchboard_isp_info.invoice_street"
    )
    switchboard_isp_info_invoice_zip_code = fields.Char(
        related="switchboard_isp_info.invoice_zip_code"
    )
    switchboard_isp_info_invoice_city = fields.Char(
        related="switchboard_isp_info.invoice_city"
    )
    switchboard_isp_info_invoice_state_id = fields.Many2one(
        "res.country.state", related="switchboard_isp_info.invoice_state_id"
    )
    switchboard_isp_info_delivery_street = fields.Char(
        related="switchboard_isp_info.delivery_street"
    )
    switchboard_isp_info_delivery_zip_code = fields.Char(
        related="switchboard_isp_info.delivery_zip_code"
    )
    switchboard_isp_info_delivery_city = fields.Char(
        related="switchboard_isp_info.delivery_city"
    )
    switchboard_isp_info_delivery_state_id = fields.Many2one(
        "res.country.state", related="switchboard_isp_info.delivery_state_id"
    )
    switchboard_isp_info_has_sim = fields.Boolean(
        related="switchboard_isp_info.has_sim",
    )
    has_mobile = fields.Boolean(related="switchboard_isp_info.has_mobile")
    has_landline = fields.Boolean(
        compute="_compute_has_landline",
    )

    @api.depends("product_id")
    def _compute_is_switchboard(self):
        service_SB = self.env.ref("switchboard_somconnexio.switchboard_category")
        for record in self:
            record.is_switchboard = (
                service_SB.id == record.product_id.product_tmpl_id.categ_id.id
            )

    @api.depends("product_id")
    def _compute_has_landline(self):
        """
        Check if product is is SB landline product
        """
        landline_product = self.env.ref("switchboard_somconnexio.FixCentraletaVirtual")
        for record in self:
            record.has_landline = record.product_id == landline_product

    @api.onchange("switchboard_isp_info_icc")
    def _onchange_switchboard_icc(self):
        icc_change = {"icc": self.switchboard_isp_info_icc}
        if isinstance(self.id, models.NewId):
            self._origin.switchboard_isp_info.write(icc_change)
        else:
            self.switchboard_isp_info.write(icc_change)

    @api.constrains("is_switchboard", "switchboard_isp_info")
    def _check_isp_info(self):
        for record in self:
            if record.is_switchboard and not record.switchboard_isp_info:
                raise ValidationError(
                    _(
                        "A switchboard lead line needs a Switchboard "
                        + "ISP Info instance related."
                    )
                )

    @api.depends("switchboard_isp_info_type")
    def _compute_crm_creation_reason(self):
        super(CRMLeadLine, self)._compute_crm_creation_reason()
        for line in self:
            if not line.create_reason and line.switchboard_isp_info_type:
                line.create_reason = line.switchboard_isp_info_type

    def _get_formview_id(self):
        if self.env.context.get("is_switchboard"):
            return self.env.ref(
                "switchboard_somconnexio.view_form_lead_line_switchboard"
            ).id
        return super(CRMLeadLine, self)._get_formview_id()

    def _compute_external_provisioning_required(self):
        """
        Check if the line has switchboard additional products, as mobiles,
        that may require external provisioning.
        :return: Boolean
        """
        super()._compute_external_provisioning_required()
        for line in self:
            if line.is_switchboard:
                if line.has_mobile or line.has_landline:
                    line.external_provisioning_required = True
                else:
                    line.external_provisioning_required = False

    def create_switchboard_contract(self, date_start):
        """
        Create a switchboard contract from a lead line
        :param date_start: Start date for the contract invoicing
        :return: Contract record
        """

        if not self.is_switchboard:
            raise ValidationError(_("This lead line is not a switchboard service."))
        if self.has_mobile or self.has_landline:
            raise ValidationError(
                _("This SB lead line has either a mobile or landline associated.")
            )

        supplier_id = self.env.ref("switchboard_somconnexio.service_supplier_enreach")
        contract_vals = self._prepare_contract_vals_from_line(supplier_id)
        switchboard_contract_service_info = (
            self._create_switchboard_contract_service_info()
        )
        contract_vals[
            "switchboard_service_contract_info_id"
        ] = switchboard_contract_service_info.id
        if self.switchboard_isp_info.additional_product_ids:
            for product in self.switchboard_isp_info.additional_product_ids:
                contract_line_vals = self._prepare_contract_line_vals(
                    product, date_start
                )
                contract_vals["contract_line_ids"].append((0, 0, contract_line_vals))

        contract = self.env["contract.contract"].create(contract_vals)

        return contract

    def _create_switchboard_contract_service_info(self):
        """
        Create the switchboard contract service information.
        This method is only called for agents without mobiles.
        :return: Switchboard contract service information record
        """
        switchboard_service_info = (
            self.env["switchboard.service.contract.info"]
            .sudo()
            .create(
                {
                    "agent_name": self.switchboard_isp_info.agent_name,
                    "agent_email": self.switchboard_isp_info.agent_email,
                    "extension": self.switchboard_isp_info.extension,
                }
            )
        )

        return switchboard_service_info

    def _prepare_contract_line_vals(self, product, date_start):
        """
        Prepare the contract line values from the product.
        :param product: Product record
        :param date_start: Start date for the contract line
        :return: Dictionary of contract line values
        """
        return {
            "name": product.name,
            "product_id": product.id,
            "date_start": date_start,
        }
