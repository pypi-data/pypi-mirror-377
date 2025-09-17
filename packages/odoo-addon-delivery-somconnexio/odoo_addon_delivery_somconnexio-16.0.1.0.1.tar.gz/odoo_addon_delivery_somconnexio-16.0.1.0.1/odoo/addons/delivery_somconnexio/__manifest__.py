{
    "name": "Odoo Som Connexió Delivery processes customizations",
    "version": "16.0.1.0.1",
    "summary": """
        Customizations for delivery processes in Som Connexió, ensuring seamless
        integration with logistics.
    """,
    "author": "Coopdevs Treball SCCL, Som Connexió SCCL",
    "website": "https://coopdevs.org",
    "license": "AGPL-3",
    "category": "Cooperative management",
    "depends": ["component", "somconnexio"],
    "data": [
        "data/crm_stage_data.xml",
        "views/crm_lead.xml",
        "crons/crm_track_correos_delivery_cron.xml",
        "wizards/crm_lead_generate_SIM_delivery/crm_lead_generate_SIM_delivery.xml",
        "wizards/crm_lead_print_SIM_delivery_label/crm_lead_print_SIM_delivery_label.xml",  # noqa: E501
        "security/ir.model.access.csv",
    ],
    "demo": [],
    "external_dependencies": {},
    "application": False,
    "installable": True,
}
