# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    _rec_names_search = ['name', 'partner_id', 'contact_name', 'partner_name', 'phone']

    @api.depends('name', 'partner_id', 'partner_id.name', 'contact_name', 'partner_name', 'phone')
    def _compute_display_name(self):
        for lead in self:
            lead_name = (lead.name or '').strip()
            customer = (lead.partner_id.name or '').strip() or (lead.contact_name or '').strip() or (lead.partner_name or '').strip()
            details = []
            if customer and customer.lower() not in lead_name.lower():
                details.append(customer)
            if lead.phone and lead.phone.strip() not in lead_name and lead.phone.strip() not in customer:
                details.append(lead.phone.strip())

            if details and lead_name:
                lead.display_name = f"{lead_name} - {', '.join(details)}"
            elif details:
                lead.display_name = ', '.join(details)
            else:
                lead.display_name = lead_name or ''

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
            ('overdue', 'Overdue / Surpassed Deadline'),
            ('done', 'Visited / Done'),
            ('cancelled', 'Cancelled'),
        ],
        string='Site Visit Status',
        compute='_compute_site_visits',
        store=True
    )

    @api.depends('site_visit_ids', 'site_visit_ids.state', 'site_visit_ids.date_booked', 'site_visit_ids.is_overdue')
    def _compute_site_visits(self):
        for lead in self:
            lead.site_visit_count = len(lead.site_visit_ids)
            if not lead.site_visit_ids:
                lead.site_visit_state = 'none'
            else:
                open_visits = lead.site_visit_ids.filtered(lambda v: v.state in ('open', 'rescheduled'))
                if open_visits:
                    if any(v.is_overdue for v in open_visits):
                        lead.site_visit_state = 'overdue'
                    else:
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



