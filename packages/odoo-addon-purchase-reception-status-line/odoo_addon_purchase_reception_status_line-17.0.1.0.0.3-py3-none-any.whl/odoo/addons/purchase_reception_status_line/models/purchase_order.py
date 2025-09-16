# Copyright 2024 ForgeFlow (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    force_received = fields.Boolean(
        compute="_compute_force_received",
        inverse="_inverse_force_received",
        store=True,
        tracking=True,
        help="If true, the order is marked forced only when all lines "
        "are fully received and at least one line was manually forced.",
    )

    @api.depends("order_line.receipt_status", "order_line.force_received")
    def _compute_force_received(self):
        for po in self:
            all_received = all(line.receipt_status == "full" for line in po.order_line)
            any_forced = any(line.force_received for line in po.order_line)
            po.force_received = all_received and any_forced

    def _inverse_force_received(self):
        for po in self:
            if po.force_received:
                to_force = po.order_line.filtered(
                    lambda line: line.receipt_status != "full"
                )
                to_force.write({"force_received": True})
            else:
                forced_lines = po.order_line.filtered(lambda line: line.force_received)
                forced_lines.write({"force_received": False})
                forced_lines._compute_receipt_status()

    @api.depends(
        "state",
        "force_received",
        "order_line.qty_received",
        "order_line.product_qty",
        "order_line.force_received",
        "order_line.receipt_status",
    )
    def _compute_oca_receipt_status(self):
        result = super()._compute_oca_receipt_status()
        for order in self.filtered(lambda po: po.receipt_status != "full"):
            status = order.receipt_status
            if order.state in ("purchase", "done"):
                if all([line.receipt_status == "full" for line in order.order_line]):
                    status = "full"
                elif any(
                    [
                        line.receipt_status in ["full", "partial"]
                        for line in order.order_line
                    ]
                ):
                    status = "partial"
            order.receipt_status = status
        return result
