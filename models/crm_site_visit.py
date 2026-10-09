# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CrmSiteVisit(models.Model):
    _name = 'crm.site.visit'
    _description = 'CRM Site Visit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_booked desc, id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    lead_id = fields.Many2one(
        'crm.lead',
        string='Lead / Opportunity',
        ondelete='cascade',
        index=True,
        tracking=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer / Company',
        store=True,
        index=True,
        tracking=True
    )
    address = fields.Text(
        string='Site Address',
        tracking=True,
        help='Physical location or address for the site visit.'
    )
    date_booked = fields.Datetime(
        string='Date Booked',
        required=True,
        default=fields.Datetime.now,
        tracking=True
    )
    original_date = fields.Datetime(
        string='Original Date Booked',
        readonly=True,
        copy=False,
        help='Initial scheduled date before any reschedules.'
    )
    user_id = fields.Many2one(
        'res.users',
        string='Person Going',
        default=lambda self: self.env.user,
        tracking=True,
        domain="[('share', '=', False), ('active', '=', True)]"
    )

    state = fields.Selection([
        ('open', 'Open / Scheduled'),
        ('rescheduled', 'Rescheduled'),
        ('done', 'Visited / Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='open', required=True, tracking=True, index=True)

    reschedule_count = fields.Integer(
        string='Reschedule Count',
        default=0,
        readonly=True,
        copy=False,
        help='Number of times the visit was rescheduled.'
    )
    reschedule_reason = fields.Text(
        string='Last Reschedule Reason',
        copy=False,
        tracking=True
    )

    # --- Visit Execution & Outcome Fields (populated once visit occurs) ---
    actual_visitor_id = fields.Many2one(
        'res.users',
        string='Person Who Went',
        tracking=True,
        domain="[('share', '=', False), ('active', '=', True)]"
    )
    date_visited = fields.Datetime(
        string='Date Visited',
        tracking=True
    )
    people_seen_count = fields.Integer(
        string='Number of Persons Seen',
        tracking=True,
        help='Number of client representatives or individuals met at the site.'
    )
    notes = fields.Html(
        string='Brief Notes / Visit Summary',
        tracking=True
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        lead_id = res.get('lead_id') or self.env.context.get('default_lead_id')
        if not lead_id and self.env.context.get('active_model') == 'crm.lead':
            lead_id = self.env.context.get('active_id')
        if lead_id:
            lead = self.env['crm.lead'].browse(lead_id)
            if lead.exists():
                if 'lead_id' in fields_list and not res.get('lead_id'):
                    res['lead_id'] = lead.id
                if 'partner_id' in fields_list and not res.get('partner_id') and lead.partner_id:
                    res['partner_id'] = lead.partner_id.id
                if 'address' in fields_list and not res.get('address'):
                    addr_parts = [p for p in [lead.street, lead.street2, lead.city] if p]
                    if addr_parts:
                        res['address'] = ', '.join(addr_parts)
        return res

    @api.onchange('lead_id')
    def _onchange_lead_id(self):
        if self.lead_id:
            if self.lead_id.partner_id and not self.partner_id:
                self.partner_id = self.lead_id.partner_id
            if not self.address:
                addr_parts = [p for p in [self.lead_id.street, self.lead_id.street2, self.lead_id.city] if p]
                if addr_parts:
                    self.address = ', '.join(addr_parts)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('crm.site.visit') or _('New')
            if 'date_booked' in vals and not vals.get('original_date'):
                vals['original_date'] = vals['date_booked']
            # Default partner_id and address from lead if blank
            if vals.get('lead_id'):
                lead = self.env['crm.lead'].browse(vals['lead_id'])
                if lead.exists():
                    if not vals.get('partner_id') and lead.partner_id:
                        vals['partner_id'] = lead.partner_id.id
                    if not vals.get('address'):
                        addr_parts = [p for p in [lead.street, lead.street2, lead.city] if p]
                        if addr_parts:
                            vals['address'] = ', '.join(addr_parts)
        return super().create(vals_list)

    def action_mark_done(self):
        """Mark site visit as completed / visited."""
        for record in self:
            vals = {'state': 'done'}
            if not record.date_visited:
                vals['date_visited'] = fields.Datetime.now()
            if not record.actual_visitor_id:
                vals['actual_visitor_id'] = record.user_id or self.env.user
            record.write(vals)
            record.message_post(
                body=_("Site visit marked as <b>Completed / Visited</b> by %s.") % (record.actual_visitor_id.name or self.env.user.name),
                subtype_xmlid='mail.mt_note'
            )

    def action_set_open(self):
        """Reopen site visit."""
        for record in self:
            record.write({'state': 'open'})
            record.message_post(body=_("Site visit status reset to Open / Scheduled."))

    def action_cancel(self):
        """Cancel site visit."""
        for record in self:
            record.write({'state': 'cancelled'})
            record.message_post(body=_("Site visit cancelled."))

    def action_open_reschedule_wizard(self):
        """Open popup wizard to record new date and reason for rescheduling."""
        self.ensure_one()
        return {
            'name': _('Reschedule Site Visit'),
            'type': 'ir.actions.act_window',
            'res_model': 'crm.site.visit.reschedule.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_visit_id': self.id,
                'default_new_date': self.date_booked,
                'default_person_going_id': self.user_id.id if self.user_id else False,
            }
        }
