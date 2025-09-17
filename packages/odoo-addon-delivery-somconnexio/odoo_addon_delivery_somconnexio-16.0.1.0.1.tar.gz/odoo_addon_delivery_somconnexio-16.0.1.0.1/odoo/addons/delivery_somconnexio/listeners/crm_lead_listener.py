from odoo.addons.component.core import Component


class CrmLeadListener(Component):
    _inherit = "crm.lead.listener"

    def on_record_write(self, record, fields=None):
        delivery_stage = self.env.ref("delivery_somconnexio.stage_lead8")
        if (
            "stage_id" in fields and record.stage_id == delivery_stage
        ):  # Stage Generating delivery
            record.with_delay().create_shipment()
