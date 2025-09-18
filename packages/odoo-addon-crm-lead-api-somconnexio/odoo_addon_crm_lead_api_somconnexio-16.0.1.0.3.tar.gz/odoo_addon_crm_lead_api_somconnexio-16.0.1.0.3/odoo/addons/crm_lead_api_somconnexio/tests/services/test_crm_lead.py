import json
import odoo
from odoo.addons.base_rest_somconnexio.tests.common_service import BaseRestCaseAdmin
from odoo.addons.switchboard_somconnexio.tests.helper_service import crm_lead_create
import logging

_logger = logging.getLogger(__name__)


class CRMLeadServiceTestCase(BaseRestCaseAdmin):
    def setUp(self):
        super().setUp()
        self.partner = self.env.ref("somconnexio.res_partner_1_demo")
        self.url = "/api/crm-lead"
        self.activate_url = "/public-api/crm-lead/activate"
        self.product_mobile = self.env.ref("somconnexio.150Min1GB")
        self.ba_data = {
            "partner_id": self.partner.ref,
            "iban": "ES6621000418401234567891",
            "phone": "700284835",
            "lead_line_ids": [
                {
                    "product_code": (
                        self.browse_ref("somconnexio.Fibra600Mb").default_code
                    ),
                    "mobile_isp_info": {},
                    "broadband_isp_info": {
                        "type": "portability",
                        "delivery_address": {
                            "street": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B",
                        },
                        "service_address": {
                            "street": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B",
                        },
                        "previous_provider": 39,
                        "previous_service": "adsl",
                        "previous_owner_name": "Newus",
                        "previous_owner_first_name": "Borgo",
                        "previous_owner_vat_number": "29461336S",
                        "previous_contract_type": "contract",
                    },
                }
            ],
        }
        self.mbl_data = {
            "partner_id": self.partner.ref,
            "iban": "ES6621000418401234567891",
            "phone": None,
            "lead_line_ids": [
                {
                    "product_code": self.product_mobile.default_code,
                    "mobile_isp_info": {
                        "icc_donor": "123",
                        "phone_number": "123",
                        "type": "portability",
                        "delivery_address": {
                            "street": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B",
                        },
                        "previous_provider": 1,
                        "previous_owner_name": "Newus",
                        "previous_owner_first_name": "Borgo",
                        "previous_owner_vat_number": "29461336S",
                        "previous_contract_type": "contract",
                    },
                    "broadband_isp_info": {},
                }
            ],
        }
        self.switchboard_data = {
            "partner_id": self.partner.ref,
            "iban": "ES6621000418401234567891",
            "phone": None,
            "lead_line_ids": [
                {
                    "product_code": (
                        self.browse_ref(
                            "switchboard_somconnexio.AgentCentraletaVirtualApp500"
                        ).default_code
                    ),
                    "mobile_isp_info": {},
                    "broadband_isp_info": {},
                    "switchboard_isp_info": {
                        "type": "new",
                        "mobile_phone_number": "123456789",
                        "agent_name": "Agent Name",
                        "agent_email": "some_mail@test.coop",
                        "extension": "1234",
                        "icc": "12345678901234567890123456789012",
                    },
                }
            ],
        }

    def test_route_right_create(self):
        partner = self.browse_ref("somconnexio.res_partner_2_demo")
        data = {
            "partner_id": partner.ref,
            "iban": "ES6621000418401234567891",
            "phone": None,
            "email": None,
            "lead_line_ids": [
                {
                    "product_code": self.product_mobile.default_code,
                    "mobile_isp_info": {
                        "icc_donor": "123",
                        "phone_number": "123",
                        "type": "portability",
                        "delivery_address": {
                            "street": "Carrer del Rec",
                            "street2": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B",
                        },
                        "invoice_address": {
                            "street": "Carrer del Rec",
                            "street2": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B",
                        },
                        "previous_provider": 1,
                        "previous_owner_name": "Newus",
                        "previous_owner_first_name": "Borgo",
                        "previous_owner_vat_number": "29461336S",
                        "previous_contract_type": "contract",
                    },
                    "broadband_isp_info": {},
                }
            ],
        }
        response = self.http_post(self.url, data=data)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        (crm_lead,) = self.env["crm.lead"].browse(content["id"])
        self.assertEqual(
            crm_lead.partner_id.id,
            partner.id,
        )
        self.assertEqual(len(crm_lead.lead_line_ids), 1)
        self.assertEqual(crm_lead.lead_line_ids[0].iban, data["iban"])
        self.assertEqual(crm_lead.lead_line_ids[0].mobile_isp_info.phone_number, "123")
        self.assertEqual(
            crm_lead.team_id.id, self.env.ref("somconnexio.residential").id
        )
        crm_lead_line = crm_lead.lead_line_ids[0]
        self.assertEqual(
            crm_lead_line.product_id.id, self.browse_ref("somconnexio.150Min1GB").id
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.icc_donor,
            "123",
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.type,
            "portability",
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.delivery_full_street,
            "Carrer del Rec 123",
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.delivery_city,
            "Barcelona",
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.delivery_zip_code,
            "08000",
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.delivery_country_id.id,
            self.browse_ref("base.es").id,
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.delivery_state_id.id,
            self.browse_ref("base.state_es_b").id,
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.invoice_full_street,
            "Carrer del Rec 123",
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.invoice_city,
            "Barcelona",
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.invoice_zip_code,
            "08000",
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.invoice_country_id.id,
            self.browse_ref("base.es").id,
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.invoice_state_id.id,
            self.browse_ref("base.state_es_b").id,
        )
        self.assertFalse(crm_lead.phone)
        self.assertEqual(crm_lead.email_from, partner.email)

    def test_route_right_create_with_partner_id(self):
        data = self.mbl_data.copy()
        response = self.http_post(self.url, data=data)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        (crm_lead,) = self.env["crm.lead"].browse(content["id"])
        self.assertEqual(crm_lead.partner_id.ref, self.partner.ref)

    def test_route_right_create_with_icc(self):
        data = self.mbl_data.copy()
        data["lead_line_ids"][0]["mobile_isp_info"]["icc"] = "123"

        response = self.http_post(self.url, data=data)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        (crm_lead,) = self.env["crm.lead"].browse(content["id"])
        self.assertTrue(crm_lead.lead_line_ids[0].mobile_isp_info.has_sim)

    def test_route_right_create_with_partner_id_without_previous_owner(self):
        data = self.mbl_data.copy()
        for key in [
            "previous_owner_name",
            "previous_owner_first_name",
            "previous_owner_vat_number",
        ]:
            del data["lead_line_ids"][0]["mobile_isp_info"][key]

        response = self.http_post(self.url, data=data)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        crm_lead = self.env["crm.lead"].browse(content["id"])
        self.assertEqual(crm_lead.partner_id.ref, self.partner.ref)

    def test_route_right_create_broadband_portability_without_fix(self):
        response = self.http_post(self.url, data=self.ba_data)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        (crm_lead,) = self.env["crm.lead"].browse(content["id"])
        crm_lead_line = crm_lead.lead_line_ids[0]

        self.assertEqual(crm_lead.phone, "700284835")
        self.assertTrue(crm_lead_line.broadband_isp_info.no_previous_phone_number)
        self.assertEqual(crm_lead_line.broadband_isp_info.phone_number, "-")
        self.assertEqual(crm_lead_line.broadband_isp_info.previous_service, "adsl")

    def test_route_right_create_broadband_portability_with_fix(self):
        self.ba_data["lead_line_ids"][0]["broadband_isp_info"][
            "phone_number"
        ] = "98787889"
        response = self.http_post(self.url, data=self.ba_data)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        crm_lead = self.env["crm.lead"].browse(content["id"])
        crm_lead_line = crm_lead.lead_line_ids[0]

        self.assertTrue(crm_lead_line.broadband_isp_info.keep_phone_number)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_broadband_empty_previous_service(self):
        # Empty previous_service
        self.ba_data.get("lead_line_ids")[0].get("broadband_isp_info")[
            "previous_service"
        ] = ""

        response = self.http_post(self.url, data=self.ba_data)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        (crm_lead,) = self.env["crm.lead"].browse(content["id"])
        crm_lead_line = crm_lead.lead_line_ids[0]

        self.assertFalse(crm_lead_line.broadband_isp_info.previous_service)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_broadband_bad_previous_service(self):
        # Update previous_service
        self.ba_data.get("lead_line_ids")[0].get("broadband_isp_info")[
            "previous_service"
        ] = "fake-service"

        response = self.http_post(self.url, data=self.ba_data)

        self.assertEqual(response.status_code, 400)
        error_msg = response.json().get("description")
        self.assertRegex(error_msg, "BadRequest")

    def test_route_right_create_switchboard_isp_info_create(self):
        data = self.switchboard_data.copy()
        sb_isp_info_data = data["lead_line_ids"][0]["switchboard_isp_info"]
        response = self.http_post(self.url, data=data)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        (crm_lead,) = self.env["crm.lead"].browse(content["id"])
        crm_lead_line = crm_lead.lead_line_ids[0]
        self.assertEqual(
            crm_lead_line.switchboard_isp_info.mobile_phone_number,
            sb_isp_info_data["mobile_phone_number"],
        )
        self.assertEqual(
            crm_lead_line.switchboard_isp_info.agent_name,
            sb_isp_info_data["agent_name"],
        )
        self.assertEqual(
            crm_lead_line.switchboard_isp_info.agent_email,
            sb_isp_info_data["agent_email"],
        )
        self.assertEqual(
            crm_lead_line.switchboard_isp_info.extension,
            sb_isp_info_data["extension"],
        )
        self.assertEqual(
            crm_lead_line.switchboard_isp_info.icc,
            sb_isp_info_data["icc"],
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_mobile_isp_info_create(self):
        data = {
            "partner_id": self.browse_ref("somconnexio.res_partner_2_demo").ref,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": self.product_mobile.default_code,
                    "mobile_isp_info": {},
                    "broadband_isp_info": {},
                    "switchboard_isp_info": {},
                }
            ],
        }
        response = self.http_post(self.url, data=data)
        self.assertEqual(response.status_code, 400)
        error_msg = response.json().get("description")
        self.assertRegex(
            error_msg,
            "Mobile product SE_SC_REC_MOBILE_T_150_1024 needs a mobile_isp_info",
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_broadband_isp_info_create(self):
        data = {
            "partner_id": self.browse_ref("somconnexio.res_partner_2_demo").ref,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": (
                        self.browse_ref("somconnexio.ADSL20MBSenseFix").default_code
                    ),
                    "mobile_isp_info": {},
                    "broadband_isp_info": {},
                    "switchboard_isp_info": {},
                }
            ],
        }
        response = self.http_post(self.url, data=data)
        self.assertEqual(response.status_code, 400)
        error_msg = response.json().get("description")
        self.assertRegex(
            error_msg,
            "Broadband product SE_SC_REC_BA_ADSL_SF needs a broadband_isp_info",
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_switchboard_isp_info_create(self):
        data = {
            "partner_id": self.browse_ref("somconnexio.res_partner_2_demo").ref,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": (
                        self.browse_ref(
                            "switchboard_somconnexio.AgentCentraletaVirtualApp500"
                        ).default_code
                    ),
                    "mobile_isp_info": {},
                    "broadband_isp_info": {},
                    "switchboard_isp_info": {},
                }
            ],
        }
        response = self.http_post(self.url, data=data)
        self.assertEqual(response.status_code, 400)
        error_msg = response.json().get("description")
        self.assertRegex(
            error_msg,
            "Switchboard product SE_SC_REC_CV_APP_500 needs a switchboard_isp_info",
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_wrong_without_iban(self):
        data = self.mbl_data.copy()
        data.pop("iban")

        response = self.http_post(self.url, data=data)

        self.assertEqual(response.status_code, 400)

    def test_route_right_create_with_partner_id_wo_delivery_address(self):
        data = self.mbl_data.copy()
        data["lead_line_ids"][0]["mobile_isp_info"].pop("delivery_address")

        response = self.http_post(self.url, data=data)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        crm_lead = self.env["crm.lead"].browse(content["id"])
        self.assertEqual(crm_lead.partner_id.ref, self.partner.ref)
        crm_lead_line = crm_lead.lead_line_ids[0]
        self.assertEqual(
            crm_lead_line.mobile_isp_info.delivery_street,
            self.partner.street,
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.delivery_city,
            self.partner.city,
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.delivery_zip_code,
            self.partner.zip,
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.delivery_country_id, self.partner.country_id
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.delivery_state_id, self.partner.state_id
        )

    def test_route_right_create_wo_partner_id_wo_delivery_address_w_icc(self):
        data = {
            "partner_id": self.browse_ref("somconnexio.res_partner_2_demo").ref,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": self.product_mobile.default_code,
                    "mobile_isp_info": {
                        "icc": "123",
                        "type": "new",
                    },
                    "broadband_isp_info": {},
                }
            ],
        }

        response = self.http_post(self.url, data=data)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        (crm_lead,) = self.env["crm.lead"].browse(content["id"])
        crm_lead_line = crm_lead.lead_line_ids[0]
        self.assertEqual(
            crm_lead_line.mobile_isp_info.icc,
            "123",
        )

    def test_route_right_create_adsl_wo_fix_void_phone_number(self):
        data = {
            "partner_id": self.partner.ref,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": (
                        self.browse_ref("somconnexio.ADSL20MBSenseFix").default_code
                    ),
                    "broadband_isp_info": {
                        "phone_number": "",
                        "type": "new",
                    },
                }
            ],
        }

        response = self.http_post(self.url, data=data)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        (crm_lead,) = self.env["crm.lead"].browse(content["id"])
        self.assertEqual(crm_lead.lead_line_ids.broadband_isp_info_phone_number, "-")

    def test_route_right_create_adsl_wo_fix_missing_phone_number(self):
        data = {
            "partner_id": self.partner.ref,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": (
                        self.browse_ref("somconnexio.ADSL20MBSenseFix").default_code
                    ),
                    "broadband_isp_info": {
                        "type": "new",
                    },
                }
            ],
        }

        response = self.http_post(self.url, data=data)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        (crm_lead,) = self.env["crm.lead"].browse(content["id"])
        self.assertEqual(crm_lead.lead_line_ids.broadband_isp_info_phone_number, "-")

    def test_route_right_combination_no_pack_products(self):
        mobile_product = self.browse_ref("somconnexio.150Min1GB")
        pack_fiber_product = self.browse_ref("somconnexio.Fibra100Mb")
        data = {
            "partner_id": self.browse_ref("somconnexio.res_partner_2_demo").ref,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": mobile_product.default_code,
                    "mobile_isp_info": {
                        "icc_donor": "123",
                        "phone_number": "123",
                        "type": "portability",
                        "delivery_address": {
                            "street": "Carrer del Rec",
                            "street2": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B",
                        },
                        "invoice_address": {
                            "street": "Carrer del Rec",
                            "street2": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B",
                        },
                        "previous_provider": 1,
                        "previous_owner_name": "Newus",
                        "previous_owner_first_name": "Borgo",
                        "previous_owner_vat_number": "29461336S",
                        "previous_contract_type": "contract",
                    },
                    "broadband_isp_info": {},
                },
                {
                    "product_code": pack_fiber_product.default_code,
                    "broadband_isp_info": {
                        "type": "portability",
                        "service_address": {
                            "street": "a",
                            "city": "aa",
                            "zip_code": "aaa",
                            "state": "A",
                            "country": "ES",
                        },
                        "previous_provider": 51,
                        "delivery_address": {
                            "street": "a",
                            "city": "aa",
                            "zip_code": "aaa",
                            "state": "A",
                            "country": "ES",
                        },
                        "phone_number": "937889022",
                    },
                },
            ],
        }
        response = self.http_post(self.url, data=data)
        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        crm_lead = self.env["crm.lead"].browse(content["id"])

        self.assertTrue(
            all(line.iban == data["iban"] for line in crm_lead.lead_line_ids)
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_right_combination_pack_products(self):
        mobile_product = self.browse_ref("somconnexio.TrucadesIllimitades20GBPack")
        pack_fiber_product = self.browse_ref("somconnexio.Fibra100Mb")
        data = {
            "partner_id": self.browse_ref("somconnexio.res_partner_2_demo").ref,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": mobile_product.default_code,
                    "mobile_isp_info": {
                        "icc_donor": "123",
                        "phone_number": "123",
                        "type": "portability",
                        "delivery_address": {
                            "street": "Carrer del Rec",
                            "street2": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B",
                        },
                        "invoice_address": {
                            "street": "Carrer del Rec",
                            "street2": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B",
                        },
                        "previous_provider": 1,
                        "previous_owner_name": "Newus",
                        "previous_owner_first_name": "Borgo",
                        "previous_owner_vat_number": "29461336S",
                        "previous_contract_type": "contract",
                    },
                    "broadband_isp_info": {},
                },
                {
                    "product_code": pack_fiber_product.default_code,
                    "broadband_isp_info": {
                        "type": "portability",
                        "service_address": {
                            "street": "a",
                            "city": "aa",
                            "zip_code": "aaa",
                            "state": "A",
                            "country": "ES",
                        },
                        "previous_provider": 51,
                        "delivery_address": {
                            "street": "a",
                            "city": "aa",
                            "zip_code": "aaa",
                            "state": "A",
                            "country": "ES",
                        },
                        "phone_number": "937889022",
                    },
                },
            ],
        }
        response = self.http_post(self.url, data=data)
        self.assertEqual(response.status_code, 200)

    def test_route_right_combination_pack_products_different_number(self):
        mobile_product = self.browse_ref("somconnexio.TrucadesIllimitades20GBPack")
        pack_fiber_product = self.browse_ref("somconnexio.Fibra100Mb")
        data = {
            "partner_id": self.browse_ref("somconnexio.res_partner_2_demo").ref,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": mobile_product.default_code,
                    "mobile_isp_info": {
                        "icc_donor": "123",
                        "phone_number": "123",
                        "type": "portability",
                        "delivery_address": {
                            "street": "Carrer del Rec",
                            "street2": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B",
                        },
                        "invoice_address": {
                            "street": "Carrer del Rec",
                            "street2": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B",
                        },
                        "previous_provider": 1,
                        "previous_owner_name": "Newus",
                        "previous_owner_first_name": "Borgo",
                        "previous_owner_vat_number": "29461336S",
                        "previous_contract_type": "contract",
                    },
                    "broadband_isp_info": {},
                },
                {
                    "product_code": pack_fiber_product.default_code,
                    "broadband_isp_info": {
                        "type": "portability",
                        "service_address": {
                            "street": "a",
                            "city": "aa",
                            "zip_code": "aaa",
                            "state": "A",
                            "country": "ES",
                        },
                        "previous_provider": 51,
                        "delivery_address": {
                            "street": "a",
                            "city": "aa",
                            "zip_code": "aaa",
                            "state": "A",
                            "country": "ES",
                        },
                        "phone_number": "937889022",
                    },
                },
                {
                    "product_code": pack_fiber_product.default_code,
                    "broadband_isp_info": {
                        "type": "portability",
                        "service_address": {
                            "street": "a",
                            "city": "aa",
                            "zip_code": "aaa",
                            "state": "A",
                            "country": "ES",
                        },
                        "previous_provider": 51,
                        "delivery_address": {
                            "street": "a",
                            "city": "aa",
                            "zip_code": "aaa",
                            "state": "A",
                            "country": "ES",
                        },
                        "phone_number": "937889022",
                    },
                },
            ],
        }
        response = self.http_post(self.url, data=data)
        self.assertEqual(response.status_code, 200)

    def test_route_right_combination_pack_extra_product(self):
        mobile_product = self.browse_ref("somconnexio.TrucadesIllimitades20GBPack")
        mobile_extra_product = self.browse_ref("somconnexio.TrucadesIllimitades20GB")
        pack_fiber_product = self.browse_ref("somconnexio.Fibra100Mb")
        data = {
            "partner_id": self.browse_ref("somconnexio.res_partner_2_demo").ref,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": mobile_product.default_code,
                    "mobile_isp_info": {
                        "icc_donor": "123",
                        "phone_number": "123",
                        "type": "portability",
                        "delivery_address": {
                            "street": "Carrer del Rec",
                            "street2": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B",
                        },
                        "invoice_address": {
                            "street": "Carrer del Rec",
                            "street2": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B",
                        },
                        "previous_provider": 1,
                        "previous_owner_name": "Newus",
                        "previous_owner_first_name": "Borgo",
                        "previous_owner_vat_number": "29461336S",
                        "previous_contract_type": "contract",
                    },
                    "broadband_isp_info": {},
                },
                {
                    "product_code": mobile_extra_product.default_code,
                    "mobile_isp_info": {
                        "icc_donor": "123",
                        "phone_number": "123",
                        "type": "portability",
                        "delivery_address": {
                            "street": "Carrer del Rec",
                            "street2": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B",
                        },
                        "invoice_address": {
                            "street": "Carrer del Rec",
                            "street2": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B",
                        },
                        "previous_provider": 1,
                        "previous_owner_name": "Newus",
                        "previous_owner_first_name": "Borgo",
                        "previous_owner_vat_number": "29461336S",
                        "previous_contract_type": "contract",
                    },
                    "broadband_isp_info": {},
                },
                {
                    "product_code": pack_fiber_product.default_code,
                    "broadband_isp_info": {
                        "type": "portability",
                        "service_address": {
                            "street": "a",
                            "city": "aa",
                            "zip_code": "aaa",
                            "state": "A",
                            "country": "ES",
                        },
                        "previous_provider": 51,
                        "delivery_address": {
                            "street": "a",
                            "city": "aa",
                            "zip_code": "aaa",
                            "state": "A",
                            "country": "ES",
                        },
                        "phone_number": "937889022",
                    },
                },
            ],
        }
        response = self.http_post(self.url, data=data)
        self.assertEqual(response.status_code, 200)

    def test_route_bad_single_pack_product(self):
        mobile_pack_product = self.browse_ref("somconnexio.TrucadesIllimitades20GBPack")
        data = {
            "partner_id": self.browse_ref("somconnexio.res_partner_2_demo").ref,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": mobile_pack_product.default_code,
                    "mobile_isp_info": {
                        "icc_donor": "123",
                        "phone_number": "123",
                        "type": "portability",
                        "delivery_address": {
                            "street": "Carrer del Rec",
                            "street2": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B",
                        },
                        "invoice_address": {
                            "street": "Carrer del Rec",
                            "street2": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B",
                        },
                        "previous_provider": 1,
                        "previous_owner_name": "Newus",
                        "previous_owner_first_name": "Borgo",
                        "previous_owner_vat_number": "29461336S",
                        "previous_contract_type": "contract",
                    },
                    "broadband_isp_info": {},
                }
            ],
        }
        response = self.http_post(self.url, data=data)
        self.assertEqual(response.status_code, 200)

    def test_fiber_linked_to_mobile_offer(self):
        # Create fiber contract reference
        fiber_contract = self.env.ref("somconnexio.contract_fibra_600")

        data = self.mbl_data.copy()
        data["lead_line_ids"][0]["mobile_isp_info"][
            "fiber_linked_to_mobile_offer"
        ] = fiber_contract.code

        response = self.http_post(self.url, data=data)
        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        crm_lead = self.env["crm.lead"].browse(content["id"])
        mobile_isp_info = crm_lead.lead_line_ids[0].mobile_isp_info
        self.assertEqual(mobile_isp_info.linked_fiber_contract_id, fiber_contract)

    def test_mobile_lead_with_shared_bond_id(self):
        shared_bond_id = "AAA"
        data = self.mbl_data.copy()
        data["lead_line_ids"][0]["mobile_isp_info"]["shared_bond_id"] = shared_bond_id

        response = self.http_post(self.url, data=data)
        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        crm_lead = self.env["crm.lead"].browse(content["id"])
        mobile_isp_info = crm_lead.lead_line_ids[0].mobile_isp_info
        self.assertEqual(mobile_isp_info.shared_bond_id, shared_bond_id)

    def test_route_right_create_with_tag_ids(self):
        data = self.mbl_data.copy()
        data["tag_codes"] = ["first_month_free"]

        response = self.http_post(self.url, data=data)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        crm_lead = self.env["crm.lead"].browse(content["id"])
        self.assertEqual(crm_lead.tag_ids, self.env["crm.tag"].browse(9))

    def test_route_right_create_with_email(self):
        data = self.mbl_data.copy()
        data["email"] = "test@coop.com"

        response = self.http_post(self.url, data=data)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        crm_lead = self.env["crm.lead"].browse(content["id"])
        self.assertEqual(crm_lead.email_from, "test@coop.com")

    def test_route_right_create_as_company(self):
        data = self.mbl_data.copy()
        data["is_company"] = True

        response = self.http_post(self.url, data=data)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        crm_lead = self.env["crm.lead"].browse(content["id"])
        self.assertEqual(crm_lead.team_id.id, self.env.ref("somconnexio.business").id)

    def test_route_right_create_as_company_from_n8n(self):
        data = self.mbl_data.copy()
        data["is_company"] = True
        data["is_n8n"] = True

        response = self.http_post(self.url, data=data)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        crm_lead = self.env["crm.lead"].browse(content["id"])
        self.assertEqual(crm_lead.team_id.id, self.env.ref("somconnexio.sales_n8n").id)

    def test_route_activate_success(self):
        """
        Test the successful activation of a switchboard lead.
        """
        partner = self.env.ref("somconnexio.res_partner_2_demo")
        lead = crm_lead_create(self.env, partner, "switchboard")
        lead.action_set_remesa()
        lead.action_set_won()

        self.assertEqual(lead.stage_id, self.env.ref("crm.stage_lead4"))
        self.env.cr.flush()
        self.env.invalidate_all()

        jobs_domain = [
            ("method_name", "=", "create_switchboard_contract"),
            ("model_name", "=", "crm.lead.line"),
        ]
        jobs_before = self.env["queue.job"].search_count(jobs_domain)
        self.assertFalse(jobs_before)

        data = {"lead_id": str(lead.id), "date_start": "2025-08-19"}

        response = self.http_public_post(self.activate_url, data=data)

        lead_lines = lead.lead_line_ids.filtered(
            lambda l: l.is_switchboard and not l.external_provisioning_required
        )
        jobs_after = self.env["queue.job"].search_count(jobs_domain)

        result = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["result"], "OK")
        self.assertEqual(len(lead_lines), jobs_after - jobs_before)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_activate_not_found(self):
        """
        Try to activate a non-existent lead
        """
        data = {"lead_id": "999999", "date_start": "2025-08-19"}

        response = self.http_public_post(self.activate_url, data=data)

        self.assertEqual(response.status_code, 400)
        error_msg = response.json().get("description")
        self.assertRegex(error_msg, "CRM Lead with id 999999 not found")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_activate_not_won(self):
        """
        Try to activate a non-won lead
        """
        lead = crm_lead_create(self.env, self.partner, "switchboard")
        self.assertNotEqual(lead.stage_id, self.env.ref("crm.stage_lead4"))
        data = {"lead_id": str(lead.id), "date_start": "2025-08-19"}

        response = self.http_public_post(self.activate_url, data=data)

        self.assertEqual(response.status_code, 400)
        error_msg = response.json().get("description")
        self.assertRegex(error_msg, "CRM Lead with id %s is not won" % lead.id)
