{
    "name": "CRM Lead API - SomConnexio",
    "version": "16.0.1.0.3",
    "summary": """
        Expose a REST API to create CRM Leads using the CRM Lead Som Connexió
        structure.
    """,
    "author": "Som Connexió SCCL, Coopdevs Treball SCCL",
    "website": "https://git.coopdevs.org/coopdevs/som-connexio/odoo/odoo-somconnexio",
    "license": "AGPL-3",
    "category": "Cooperative Management",
    "depends": [
        "base_rest_somconnexio",
        "cooperator_somconnexio",
        "switchboard_somconnexio",
        "somconnexio",
    ],
    "data": ["data/crm_tag.xml"],
    "demo": [],
    "external_dependencies": {},
    "application": False,
    "installable": True,
}
