from odoo.addons.base_rest_somconnexio.services.validator_helper import (
    date_validator,
    integer_validator,
)
from odoo.addons.somconnexio.services.schemas import S_ADDRESS_CREATE


S_ISP_INFO_CREATE = {
    "phone_number": {"type": "string"},
    "type": {"type": "string"},
    "delivery_address": {"nullable": True, "type": "dict", "schema": S_ADDRESS_CREATE},
    "invoice_address": {"type": "dict", "schema": S_ADDRESS_CREATE},
    "previous_provider": {"type": "integer"},
    "previous_owner_vat_number": {"type": "string"},
    "previous_owner_name": {"type": "string"},
    "previous_owner_first_name": {"type": "string"},
}

S_MOBILE_ISP_INFO_CREATE = {
    "icc": {"type": "string"},
    "icc_donor": {"type": "string"},
    "previous_contract_type": {"type": "string"},
    "fiber_linked_to_mobile_offer": {"type": "string"},
    "shared_bond_id": {"empty": True},
}

S_BROADBAND_ISP_INFO_CREATE = {
    "service_address": {"type": "dict", "schema": S_ADDRESS_CREATE},
    "keep_phone_number": {"type": "boolean"},
    "previous_service": {"type": "string", "allowed": ["", "adsl", "fiber", "4G"]},
}

S_CRM_LEAD_ACTIVATE = {
    "lead_id": {"type": "string", "check_with": integer_validator},
    "start_date": {"type": "string", "check_with": date_validator},
}

S_SWITCHBOARD_ISP_INFO_CREATE = {
    "mobile_phone_number": {"type": "string"},
    "agent_name": {"type": "string"},
    "agent_email": {"type": "string"},
    "extension": {"type": "string"},
    "icc": {"type": "string"},
}

S_CRM_LEAD_RETURN_CREATE = {"id": {"type": "integer"}}

S_CRM_LEAD_CREATE = {
    "iban": {"type": "string", "required": True, "empty": False},
    "phone": {"type": "string", "nullable": True},
    "email": {"type": "string", "nullable": True},
    "tag_codes": {"type": "list", "schema": {"type": "string"}, "nullable": True},
    "is_company": {"type": "boolean"},
    "is_n8n": {"type": "boolean"},
    "partner_id": {
        "type": "string",
        "empty": False,
        "required": True,
    },
    "lead_line_ids": {
        "type": "list",
        "empty": False,
        "schema": {
            "type": "dict",
            "schema": {
                "product_code": {"type": "string", "required": True},
                "broadband_isp_info": {
                    "type": "dict",
                    # Merging dicts in Python 3.5+
                    # https://www.python.org/dev/peps/pep-0448/
                    "schema": {
                        **S_ISP_INFO_CREATE,
                        **S_BROADBAND_ISP_INFO_CREATE,
                    },
                },
                "mobile_isp_info": {
                    "type": "dict",
                    "schema": {**S_ISP_INFO_CREATE, **S_MOBILE_ISP_INFO_CREATE},  # noqa
                },
                "switchboard_isp_info": {
                    "type": "dict",
                    "schema": {**S_ISP_INFO_CREATE, **S_SWITCHBOARD_ISP_INFO_CREATE},
                },
            },
        },
    },
}
