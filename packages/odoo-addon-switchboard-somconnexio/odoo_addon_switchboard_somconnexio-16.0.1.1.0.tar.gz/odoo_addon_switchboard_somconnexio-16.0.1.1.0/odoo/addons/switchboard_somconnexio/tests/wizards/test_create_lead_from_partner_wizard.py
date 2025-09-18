
from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class TestCreateLeadfromPartnerWizard(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner = self.browse_ref("somconnexio.res_partner_company_demo")
        self.email = self.env["res.partner"].create(
            {
                "parent_id": self.partner.id,
                "email": "new_email@test.com",
                "type": "contract-email",
            }
        )
        self.landline_sb_product = self.env.ref(
            "switchboard_somconnexio.FixCentraletaVirtual"
        )
        self.sb_categ = self.env.ref("switchboard_somconnexio.switchboard_category")

    def test_create_switchboard_lead_company(self):
        """
        Test creating a lead from a partner with switchboard technology
        """
        wizard = (
            self.env["partner.create.lead.wizard"]
            .with_context(active_id=self.partner.id)
            .create(
                {
                    "source": "others",
                    "bank_id": self.partner.bank_ids[0].id,
                    "email_id": self.email.id,
                    "phone_contact": "882828282",
                    "product_categ_id": self.sb_categ.id,
                    "product_id": self.landline_sb_product.id,
                    "type": "portability",
                    "landline": "972972972",
                    "previous_owner_vat_number": "ES12345678Z",
                    "previous_owner_name": "Lynn",
                    "previous_owner_first_name": "Margulis",
                }
            )
        )

        self.assertTrue(self.partner.is_company)
        self.assertTrue(self.sb_categ in wizard.available_product_categories)
        self.assertIn(
            self.landline_sb_product,
            wizard.available_products,
        )
        # as long as no other products are available
        self.assertEqual(len(wizard.available_products), 1)

        crm_lead_action = wizard.create_lead()
        crm_lead = self.env["crm.lead"].browse(crm_lead_action["res_id"])
        crm_lead_line = crm_lead.lead_line_ids[0]

        self.assertEqual(
            crm_lead_action.get("xml_id"),
            "somconnexio.crm_case_form_view_pack",
        )

        self.assertEqual(crm_lead.partner_id, self.partner)
        self.assertEqual(crm_lead.email_from, self.email.email)
        self.assertEqual(crm_lead_line.product_id, wizard.product_id)
        self.assertEqual(crm_lead_line.switchboard_isp_info.type, "portability")
        self.assertEqual(
            crm_lead_line.switchboard_isp_info.previous_owner_vat_number,
            wizard.previous_owner_vat_number,
        )
        self.assertEqual(
            crm_lead_line.switchboard_isp_info.previous_owner_name,
            wizard.previous_owner_name,
        )
        self.assertEqual(
            crm_lead_line.switchboard_isp_info.previous_owner_first_name,
            wizard.previous_owner_first_name,
        )
        self.assertEqual(crm_lead_line.switchboard_isp_info.icc, wizard.icc)
        self.assertEqual(
            crm_lead_line.switchboard_isp_info.phone_number, wizard.landline
        )

    def test_create_switchboard_lead_particular(self):
        """
        Test creating a lead from a partner with switchboard technology
        """

        partner = self.env.ref("somconnexio.res_partner_2_demo")
        email = self.env["res.partner"].create(
            {
                "parent_id": partner.id,
                "email": "new_email@test.com",
                "type": "contract-email",
            }
        )
        fiber_product = self.env.ref("somconnexio.Fibra600Mb")

        wizard = (
            self.env["partner.create.lead.wizard"]
            .with_context(active_id=partner.id)
            .create(
                {
                    "source": "others",
                    "bank_id": partner.bank_ids.id,
                    "email_id": email.id,
                    "phone_contact": partner.phone,
                    "product_categ_id": fiber_product.product_tmpl_id.categ_id.id,
                    "product_id": fiber_product.id,
                    "type": "new",
                }
            )
        )
        self.assertFalse(partner.is_company)
        self.assertFalse(self.sb_categ in wizard.available_product_categories)
