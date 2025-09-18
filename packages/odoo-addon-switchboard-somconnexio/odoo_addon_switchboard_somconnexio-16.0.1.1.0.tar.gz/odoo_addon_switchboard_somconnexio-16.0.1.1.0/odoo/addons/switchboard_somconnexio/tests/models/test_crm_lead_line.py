from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from ..helper_service import crm_lead_create
from odoo.exceptions import ValidationError
from datetime import date


class CRMLeadLineTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner_id = self.browse_ref("somconnexio.res_partner_2_demo")
        self.partner_iban = self.partner_id.bank_ids[0].sanitized_acc_number
        self.product_sb = self.env.ref(
            "switchboard_somconnexio.AgentCentraletaVirtualApp500"
        )
        self.product_landline = self.env.ref(
            "switchboard_somconnexio.FixCentraletaVirtual"
        )

        self.crm_lead_line_args = {
            "name": "Test SB CRM Lead Line",
            "product_id": self.product_sb.id,
            "mobile_isp_info": None,
            "broadband_isp_info": None,
            "switchboard_isp_info": None,
            "iban": self.partner_iban,
        }
        self.switchboard_isp_info_args = {
            "type": "new",
            "agent_name": "Test Agent",
            "extension": "123456789",
        }

    def test_sb_lead_line_creation_ok(self):
        switchboard_isp_info = self.env["switchboard.isp.info"].create(
            self.switchboard_isp_info_args
        )
        self.crm_lead_line_args.update(
            {
                "switchboard_isp_info": switchboard_isp_info.id,
            }
        )

        sb_crm_lead_line = self.env["crm.lead.line"].create([self.crm_lead_line_args])
        self.assertTrue(sb_crm_lead_line.id)
        self.assertTrue(sb_crm_lead_line.is_switchboard)
        self.assertEqual(sb_crm_lead_line.iban, self.partner_iban)
        self.assertEqual(sb_crm_lead_line.create_reason, switchboard_isp_info.type)

    def test_sb_lead_line_creation_without_sb_isp_info(self):
        self.assertRaises(
            ValidationError, self.env["crm.lead.line"].create, [self.crm_lead_line_args]
        )

    def test_external_provisioning_required_has_mobile(self):
        """
        Test that the external_provisioning_required field is True
        when SB lead line has an extra mobile product associated.
        """
        mobile_sb = self.env.ref("switchboard_somconnexio.CentraletaVirtualSIMUNL10GB")
        mbl_switchboard_isp_info_args = self.switchboard_isp_info_args.copy()
        mbl_switchboard_isp_info_args.update(
            {
                "additional_product_ids": [(4, mobile_sb.id)],
            }
        )
        switchboard_isp_info = self.env["switchboard.isp.info"].create(
            mbl_switchboard_isp_info_args
        )
        self.crm_lead_line_args.update(
            {
                "switchboard_isp_info": switchboard_isp_info.id,
            }
        )
        crm_lead_line_sb_mobile = self.env["crm.lead.line"].create(
            [self.crm_lead_line_args]
        )

        self.assertTrue(crm_lead_line_sb_mobile.has_mobile)
        self.assertTrue(crm_lead_line_sb_mobile.external_provisioning_required)

    def test_external_provisioning_required_has_landline(self):
        """
        Test that the external_provisioning_required field is True
        when SB lead line has a landline product associated.
        """
        switchboard_isp_info = self.env["switchboard.isp.info"].create(
            self.switchboard_isp_info_args
        )
        self.crm_lead_line_args.update(
            {
                "switchboard_isp_info": switchboard_isp_info.id,
                "product_id": self.product_landline.id,
            }
        )
        crm_lead_line = self.env["crm.lead.line"].create([self.crm_lead_line_args])

        self.assertTrue(crm_lead_line.has_landline)
        self.assertTrue(crm_lead_line.external_provisioning_required)

    def test_external_provisioning_required_no_mobile_no_landline(self):
        """
        Test that the external_provisioning_required field is False
        when SB lead line has no mobile or landline product associated.
        """
        switchboard_isp_info = self.env["switchboard.isp.info"].create(
            self.switchboard_isp_info_args
        )
        self.crm_lead_line_args.update(
            {
                "switchboard_isp_info": switchboard_isp_info.id,
            }
        )
        crm_lead_line = self.env["crm.lead.line"].create([self.crm_lead_line_args])

        self.assertFalse(crm_lead_line.has_landline)
        self.assertFalse(crm_lead_line.external_provisioning_required)

    def test_create_switchboard_contract_ok(self):
        """
        Test the creation of a switchboard contract from a SB crm_lead_line
        """
        date_start = date.today()
        sb_lead = crm_lead_create(self.env, self.partner_id, "switchboard")
        sb_lead_line = sb_lead.lead_line_ids[0]
        team_sb = self.env.ref(
            "switchboard_somconnexio.CentraletaVirtualIntegracioTeams"
        )
        sb_lead_line.switchboard_isp_info.write(
            {
                "additional_product_ids": [(4, team_sb.id)],
            }
        )
        sb_contract = sb_lead_line.create_switchboard_contract(date_start)

        self.assertTrue(sb_contract)
        self.assertEqual(sb_contract.partner_id, sb_lead.partner_id)
        self.assertEqual(sb_contract.crm_lead_line_id, sb_lead_line)
        self.assertEqual(sb_contract.date_start, date_start)
        self.assertEqual(
            sb_contract.service_technology_id,
            self.env.ref("switchboard_somconnexio.service_technology_switchboard"),
        )
        self.assertEqual(
            sb_contract.service_supplier_id,
            self.env.ref("switchboard_somconnexio.service_supplier_enreach"),
        )
        self.assertEqual(len(sb_contract.contract_line_ids), 2)
        self.assertTrue(sb_contract.contract_line_ids[0].date_start, date_start)
        self.assertEqual(
            sb_contract.contract_line_ids[0].product_id.id,
            self.crm_lead_line_args["product_id"],
        )
        self.assertEqual(sb_contract.contract_line_ids[1].date_start, date_start)
        self.assertEqual(sb_contract.contract_line_ids[1].product_id, team_sb)

    def test_create_switchboard_contract_with_mobile(self):
        """
        Test the creation of a switchboard contract from a SB crm_lead_line with mobile
        """
        mobile_sb = self.env.ref("switchboard_somconnexio.CentraletaVirtualSIMUNL10GB")
        mbl_switchboard_isp_info_args = self.switchboard_isp_info_args.copy()
        mbl_switchboard_isp_info_args.update(
            {
                "additional_product_ids": [(4, mobile_sb.id)],
            }
        )
        switchboard_isp_info = self.env["switchboard.isp.info"].create(
            mbl_switchboard_isp_info_args
        )
        self.crm_lead_line_args.update(
            {
                "switchboard_isp_info": switchboard_isp_info.id,
            }
        )
        sb_crm_lead_line = self.env["crm.lead.line"].create([self.crm_lead_line_args])

        self.assertTrue(sb_crm_lead_line.has_mobile)
        self.assertRaisesRegex(
            ValidationError,
            "This SB lead line has either a mobile or landline associated.",
            sb_crm_lead_line.create_switchboard_contract,
            date.today(),
        )

    def test_create_switchboard_contract_with_landline(self):
        """
        Test the creation of a switchboard contract from a SB crm_lead_line
        with landline
        """
        switchboard_isp_info = self.env["switchboard.isp.info"].create(
            self.switchboard_isp_info_args
        )
        self.crm_lead_line_args.update(
            {
                "switchboard_isp_info": switchboard_isp_info.id,
                "product_id": self.product_landline.id,
            }
        )
        sb_crm_lead_line = self.env["crm.lead.line"].create([self.crm_lead_line_args])

        self.assertTrue(sb_crm_lead_line.has_landline)
        self.assertRaisesRegex(
            ValidationError,
            "This SB lead line has either a mobile or landline associated.",
            sb_crm_lead_line.create_switchboard_contract,
            date.today(),
        )

    def test_create_switchboard_contract_no_switchboard(self):
        """
        Test the creation of a switchboard contract from a non SB crm_lead_line
        """
        lead = crm_lead_create(self.env, self.partner_id, "mobile")
        lead_line = lead.lead_line_ids[0]

        self.assertFalse(lead_line.is_switchboard)
        self.assertRaisesRegex(
            ValidationError,
            "This lead line is not a switchboard service.",
            lead_line.create_switchboard_contract,
            date.today(),
        )
