# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    fsm_location = fields.Boolean("Is a FS Location")
    fsm_person = fields.Boolean("Is a FS Worker")
    service_location_id = fields.Many2one(
        "fsm.location", string="Primary Service Location"
    )
    owned_location_ids = fields.One2many(
        "fsm.location",
        "owner_id",
        string="Owned Locations",
        domain=[("fsm_parent_id", "=", False)],
    )
    owned_location_count = fields.Integer(
        compute="_compute_owned_location_count", string="# of Owned Locations"
    )

    def _compute_owned_location_count(self):
        for partner in self:
            res = self.env["fsm.location"].search_count(
                [("owner_id", "child_of", partner.id)]
            )
            partner.owned_location_count = res

    def action_open_owned_locations(self):
        for partner in self:
            owned_location_ids = self.env["fsm.location"].search(
                [("owner_id", "child_of", partner.id)]
            )
            action = self.env["ir.actions.actions"]._for_xml_id(
                "fieldservice.action_fsm_location"
            )
            action["context"] = {}
            if len(owned_location_ids) > 1:
                action["domain"] = [("id", "in", owned_location_ids.ids)]
            elif len(owned_location_ids) == 1:
                action["views"] = [
                    (self.env.ref("fieldservice.fsm_location_form_view").id, "form")
                ]
                action["res_id"] = owned_location_ids.ids[0]
            return action
