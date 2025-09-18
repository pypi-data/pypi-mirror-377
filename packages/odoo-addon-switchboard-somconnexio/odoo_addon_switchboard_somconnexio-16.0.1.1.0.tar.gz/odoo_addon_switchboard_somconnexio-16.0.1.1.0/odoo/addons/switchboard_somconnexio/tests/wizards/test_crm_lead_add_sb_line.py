from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from unittest.mock import patch
from ..helper_service import crm_lead_create


class TestGeneralSetup(SCTestCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env.ref("somconnexio.res_partner_company_demo")
        self.bank_account = self.partner.bank_ids[0]
        self.lead = crm_lead_create(
            self.env,
            self.partner,
            service_category="switchboard",
        )
        self.Wizard = self.env["crm.lead.add.sb.line.wizard"]
        self.wizard = self.Wizard.with_context(active_id=self.lead.id).create({})
        self.main_product = self.env.ref(
            "switchboard_somconnexio.AgentCentraletaVirtualApp500"
        )
        self.mobile_product = self.env.ref(
            "switchboard_somconnexio.CentraletaVirtualSIMUNL10GB"
        )
        self.landline_product = self.env.ref(
            "switchboard_somconnexio.FixCentraletaVirtual"
        )
        self.Agent = self.env["agent.sb"]
        self.Landline = self.env["landline.sb"]


class TestCrmLeadAddSBLineWizard(TestGeneralSetup):
    def setUp(self):
        super().setUp()

    def test_wizard_default_get(self):
        """Test default_get method of the wizard"""
        self.assertEqual(self.wizard.lead_id, self.lead)

    def test_action_new_agent_view(self):
        """Test that action_new_agent opens the correct view"""
        result = self.wizard.action_new_agent()

        self.assertEqual(result["name"], "Add Agent")
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "agent.sb")
        self.assertEqual(result["view_mode"], "form")
        self.assertEqual(result["target"], "new")

    def test_action_new_landline_view(self):
        """Test that action_new_landline opens the correct view"""
        result = self.wizard.action_new_landline()

        self.assertEqual(result["name"], "Add Landline")
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "landline.sb")
        self.assertEqual(result["view_mode"], "form")
        self.assertEqual(result["target"], "new")

    def test_open_wizard(self):
        """Test _open_wizard method"""
        result = self.wizard._open_wizard()

        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["name"], "Switchboard Virtual Constructor")
        self.assertEqual(result["res_model"], "crm.lead.add.sb.line.wizard")
        self.assertEqual(result["res_id"], self.wizard.id)
        self.assertEqual(result["target"], "new")

    @patch(
        "odoo.addons.switchboard_somconnexio.wizards.crm_lead_add_sb_line.crm_lead_add_sb_line.AgentSwitchboard._create_lead_line"  # noqa: E501
    )
    @patch(
        "odoo.addons.switchboard_somconnexio.wizards.crm_lead_add_sb_line.crm_lead_add_sb_line.LandlineSwitchboard._create_lead_line"  # noqa: E501
    )
    def test_button_add_with_agents_and_landlines(
        self, mock_create_agent_line, mock_create_landline_line
    ):
        """Test button_add method with agents and landlines"""

        # Create mock agent
        agent = self.Agent.create(
            {
                "wizard_id": self.wizard.id,
                "partner_id": self.partner.id,
                "bank_id": self.partner.bank_ids[0].id,
                "agent_name": "Test Agent",
                "extension": "123",
                "product_id": self.main_product.id,
            }
        )

        # Create mock landline
        landline = self.Landline.create(
            {
                "wizard_id": self.wizard.id,
                "partner_id": self.partner.id,
                "bank_id": self.partner.bank_ids[0].id,
                "phone_number": "123456789",
                "product_id": self.landline_product.id,
            }
        )

        self.wizard.agent_line_ids = [(4, agent.id)]
        self.wizard.landline_line_ids = [(4, landline.id)]

        result = self.wizard.button_add()

        self.assertTrue(result)
        mock_create_agent_line.assert_called_once()
        mock_create_landline_line.assert_called_once()

    def test_button_cancel(self):
        """Test button_cancel method"""

        # Create mock agent an_create_lead_lined landline
        agent = self.Agent.create(
            {
                "wizard_id": self.wizard.id,
                "partner_id": self.partner.id,
                "bank_id": self.bank_account.id,
                "agent_name": "Test Agent",
                "extension": "123",
                "product_id": self.main_product.id,
            }
        )

        landline = self.Landline.create(
            {
                "wizard_id": self.wizard.id,
                "partner_id": self.partner.id,
                "bank_id": self.bank_account.id,
                "phone_number": "123456789",
                "product_id": self.landline_product.id,
            }
        )

        self.wizard.agent_line_ids = [(4, agent.id)]
        self.wizard.landline_line_ids = [(4, landline.id)]

        result = self.wizard.button_cancel()

        self.assertEqual(result["type"], "ir.actions.act_window_close")
        # Check that records are unlinked
        self.assertFalse(agent.exists())
        self.assertFalse(landline.exists())


class TestAgentSwitchboard(TestGeneralSetup):
    def setUp(self):
        super().setUp()
        self.bank_account = self.partner.bank_ids[0]
        self.agent = self.Agent.with_context(active_id=self.wizard.id).create(
            {
                "agent_name": "Test Agent",
                "extension": "123",
                "product_id": self.main_product.id,
                "bank_id": self.bank_account.id,
            }
        )

    def test_agent_default_get(self):
        """Test default_get method of agent"""

        self.assertEqual(self.agent.wizard_id, self.wizard)
        self.assertEqual(self.agent.partner_id, self.partner)

    def test_agent_product_domains(self):
        """Test product domain methods"""

        # Test main product domain
        main_domain = self.agent._main_product_domain()
        self.assertEqual(
            main_domain,
            [
                ("product_tmpl_id", "=", self.main_product.product_tmpl_id.id),
                ("id", "!=", self.landline_product.id),
            ],
        )

        # Test mobile product domain
        mobile_domain = self.agent._mobile_product_domain()
        self.assertEqual(
            mobile_domain,
            [("product_tmpl_id", "=", self.mobile_product.product_tmpl_id.id)],
        )

    def test_action_save_agent(self):
        """Test action_save_agent method
        Check that with this method the agent is added to the wizard's agent_line_ids
        """
        self.agent.wizard_id = self.wizard.id
        self.assertFalse(self.wizard.agent_line_ids)

        result = self.agent.action_save_agent()

        self.assertTrue(self.wizard.agent_line_ids)
        self.assertIn(self.agent, self.wizard.agent_line_ids)
        self.assertEqual(result["type"], "ir.actions.act_window")

    def test_action_go_back(self):
        """Test action_go_back method
        Check that it does not add the agent to the wizard's agent_line_ids
        """
        self.agent.wizard_id = self.wizard.id
        self.assertFalse(self.wizard.agent_line_ids)

        result = self.agent.action_go_back()

        self.assertFalse(self.wizard.agent_line_ids)
        self.assertEqual(result["type"], "ir.actions.act_window")

    def test_action_remove_agent(self):
        """Test action_remove_agent method
        Check that it removes the agent from the wizard's agent_line_ids"""
        # Add agent to wizard first
        self.wizard.agent_line_ids = [(4, self.agent.id)]
        self.assertTrue(self.wizard.agent_line_ids)

        result = self.agent.action_remove_agent()

        self.assertFalse(self.wizard.agent_line_ids)
        self.assertNotIn(self.agent, self.wizard.agent_line_ids)
        self.assertEqual(result["type"], "ir.actions.act_window")

    def test_action_edit_agent(self):
        """Test action_edit_agent method
        Check that it opens the agent form view"""

        result = self.agent.action_edit_agent()

        self.assertEqual(result["name"], "Edit Agent")
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "agent.sb")
        self.assertEqual(result["res_id"], self.agent.id)
        self.assertEqual(result["target"], "new")

    def test_create_lead_line(self):
        """Test _create_lead_line method
        Check that it creates a lead line with the correct data"""
        integration_product_id = self.env.ref(
            "switchboard_somconnexio.CentraletaVirtualIntegracioTeams"
        )
        agent = self.Agent.create(
            {
                "wizard_id": self.wizard.id,
                "partner_id": self.partner.id,
                "bank_id": self.bank_account.id,
                "agent_name": "New Agent",
                "agent_email": "agent@test.com",
                "extension": "123",
                "product_id": self.main_product.id,
                "mobile_product_id": self.mobile_product.id,
                "icc": "8986002211234567890",
                "integration_product_id": integration_product_id.id,
                "phone_number": "123456789",
                "provision_type": "portability",
                "previous_owner_first_name": "Previous Owner",
                "previous_owner_vat_number": "12345678Z",
                "previous_owner_name": "Previous Owner Name",
            }
        )

        agent._create_lead_line()

        new_lead_line = self.wizard.lead_id.lead_line_ids[-1]
        sb_isp_info = new_lead_line.switchboard_isp_info

        self.assertEqual(new_lead_line.product_id, self.main_product)
        self.assertEqual(new_lead_line.iban, self.bank_account.sanitized_acc_number)
        self.assertEqual(sb_isp_info.agent_name, agent.agent_name)
        self.assertEqual(sb_isp_info.agent_email, agent.agent_email)
        self.assertEqual(sb_isp_info.extension, agent.extension)
        self.assertEqual(sb_isp_info.mobile_phone_number, agent.phone_number)
        self.assertEqual(sb_isp_info.type, agent.provision_type)
        self.assertEqual(
            sb_isp_info.previous_owner_first_name, agent.previous_owner_first_name
        )
        self.assertEqual(sb_isp_info.previous_owner_name, agent.previous_owner_name)
        self.assertEqual(sb_isp_info.icc, agent.icc)
        self.assertEqual(
            sb_isp_info.previous_owner_vat_number,
            "ES" + agent.previous_owner_vat_number,
        )
        self.assertEqual(
            sb_isp_info.additional_product_ids,
            self.mobile_product + integration_product_id,
        )


class TestLandlineSwitchboard(TestGeneralSetup):
    def setUp(self):
        super().setUp()
        self.landline = (
            self.env["landline.sb"]
            .with_context(active_id=self.wizard.id)
            .create(
                {
                    "phone_number": "123456789",
                    "bank_id": self.bank_account.id,
                }
            )
        )

    def test_landline_default_get(self):
        """Test default_get method of landline"""
        self.assertEqual(self.landline.wizard_id, self.wizard)
        self.assertEqual(self.landline.partner_id, self.partner)
        self.assertEqual(self.landline.product_id, self.landline_product)

    def test_action_save_landline(self):
        """Test action_save_landline method
        Check that with this method the landline is added to the wizard's
        landline_line_ids
        """
        self.assertFalse(self.wizard.landline_line_ids)

        result = self.landline.action_save_landline()

        self.assertTrue(self.wizard.landline_line_ids)
        self.assertIn(self.landline, self.wizard.landline_line_ids)
        self.assertEqual(result["type"], "ir.actions.act_window")

    def test_action_go_back_landline(self):
        """Test action_go_back method for landline
        Check that it does not add the landline to the wizard's landline_line_ids
        """
        self.landline.wizard_id = self.wizard.id
        self.assertFalse(self.wizard.landline_line_ids)

        result = self.landline.action_go_back()

        self.assertFalse(self.wizard.landline_line_ids)
        self.assertEqual(result["type"], "ir.actions.act_window")

    def test_action_remove_landline(self):
        """Test action_remove_landline method
        Check that it removes the landline from the wizard's landline_line_ids
        """

        # Add landline to wizard first
        self.wizard.landline_line_ids = [(4, self.landline.id)]
        self.assertTrue(self.wizard.landline_line_ids)

        result = self.landline.action_remove_landline()

        self.assertNotIn(self.landline, self.wizard.landline_line_ids)
        self.assertFalse(self.wizard.landline_line_ids)
        self.assertEqual(result["type"], "ir.actions.act_window")

    def test_action_edit_landline(self):
        """Test action_edit_landline method
        Check that it opens the landline form view
        """

        result = self.landline.action_edit_landline()

        self.assertEqual(result["name"], "Edit Landline")
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "landline.sb")
        self.assertEqual(result["res_id"], self.landline.id)
        self.assertEqual(result["target"], "new")

    def test_create_lead_line(self):
        """Test _create_lead_line method
        Check that it creates a lead line with the correct data"""
        call_product_id = self.env.ref(
            "switchboard_somconnexio.CentraletaVirtualNumeracio900"
        )
        landline = self.Landline.create(
            {
                "wizard_id": self.wizard.id,
                "partner_id": self.partner.id,
                "bank_id": self.bank_account.id,
                "product_id": self.landline_product.id,
                "call_product_id": call_product_id.id,
                "phone_number": "123456789",
                "provision_type": "portability",
                "previous_owner_first_name": "Previous Owner",
                "previous_owner_vat_number": "12345678Z",
                "previous_owner_name": "Previous Owner Name",
            }
        )

        landline._create_lead_line()

        new_lead_line = self.wizard.lead_id.lead_line_ids[-1]
        sb_isp_info = new_lead_line.switchboard_isp_info

        self.assertEqual(new_lead_line.product_id, self.landline_product)
        self.assertEqual(new_lead_line.iban, self.bank_account.sanitized_acc_number)
        self.assertEqual(sb_isp_info.phone_number, landline.phone_number)
        self.assertEqual(sb_isp_info.type, landline.provision_type)
        self.assertEqual(
            sb_isp_info.previous_owner_first_name, landline.previous_owner_first_name
        )
        self.assertEqual(sb_isp_info.previous_owner_name, landline.previous_owner_name)
        self.assertEqual(
            sb_isp_info.previous_owner_vat_number,
            "ES" + landline.previous_owner_vat_number,
        )
        self.assertEqual(
            sb_isp_info.additional_product_ids,
            call_product_id,
        )
