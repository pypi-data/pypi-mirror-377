from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class TestContract(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.switchboard_contract = self.env.ref(
            "switchboard_somconnexio.contract_switchboard_app_500"
        )

    def test_contract_name(self, *args):
        phone_number = (
            self.switchboard_contract.switchboard_service_contract_info_id.phone_number
        )
        extension = (
            self.switchboard_contract.switchboard_service_contract_info_id.extension
        )
        self.assertEqual(
            self.switchboard_contract.name, f"{phone_number} - {extension}"
        )
        self.switchboard_contract.switchboard_service_contract_info_id.write(
            {"phone_number": "AAAAAAAA", "extension": "BBBBBBB"}
        )
        self.assertEqual(self.switchboard_contract.name, "AAAAAAAA - BBBBBBB")

    def test_contract_name(self, *args):
        self.switchboard_contract.switchboard_service_contract_info_id.write(
            {"phone_number": "", "extension": "CCCCCCC"}
        )
        self.assertEqual(self.switchboard_contract.name, "CCCCCCC")
