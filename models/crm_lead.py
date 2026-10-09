# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    site_visit_ids = fields.One2many(
        'crm.site.visit',
        'lead_id',
        string='Site Visits'
    )
    site_visit_count = fields.Integer(
        string='Site Visits Count',
        compute='_compute_site_visits',
        store=True
    )
    site_visit_state = fields.Selection(
        selection=[
            ('none', 'No Visits'),
            ('open', 'Open / Scheduled'),
            ('rescheduled', 'Rescheduled'),
            ('done', 'Visited / Done'),
            ('cancelled', 'Cancelled'),
        ],
        string='Site Visit Status',
        compute='_compute_site_visits',
        store=True
    )

    @api.depends('site_visit_ids', 'site_visit_ids.state')
    def _compute_site_visits(self):
        for lead in self:
            lead.site_visit_count = len(lead.site_visit_ids)
            if not lead.site_visit_ids:
                lead.site_visit_state = 'none'
            else:
                open_visits = lead.site_visit_ids.filtered(lambda v: v.state in ('open', 'rescheduled'))
                if open_visits:
                    lead.site_visit_state = open_visits[0].state
                else:
                    lead.site_visit_state = lead.site_visit_ids[0].state

    def action_view_site_visits(self):
        self.ensure_one()
        addr_parts = [p for p in [self.street, self.street2, self.city] if p]
        return {
            'name': 'Site Visits',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.site.visit',
            'view_mode': 'list,form,calendar',
            'domain': [('lead_id', '=', self.id)],
            'context': {
                'default_lead_id': self.id,
                'default_partner_id': self.partner_id.id if self.partner_id else False,
                'default_address': ', '.join(addr_parts) if addr_parts else False,
            }
        }
