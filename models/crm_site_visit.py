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
    city = fields.Char(
        string='Area / City',
        compute='_compute_city',
        store=True,
        readonly=False,
        index=True,
        tracking=True,
        help='City, suburb or area of the site visit.'
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
    user_ids = fields.Many2many(
        'res.users',
        'crm_site_visit_user_rel',
        'visit_id',
        'user_id',
        string='Persons Going',
        default=lambda self: [self.env.user.id],
        tracking=True,
        domain="[('share', '=', False), ('active', '=', True)]",
        help='Representatives or team members scheduled to attend the site visit.'
    )
    user_id = fields.Many2one(
        'res.users',
        string='Lead / Primary Person Going',
        default=lambda self: self.env.user,
        tracking=True,
        domain="[('share', '=', False), ('active', '=', True)]",
        help='Primary person responsible for leading the visit.'
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

    is_overdue = fields.Boolean(
        string='Overdue / Surpassed Deadline',
        compute='_compute_is_overdue',
        search='_search_is_overdue',
        help='True if the site visit date has passed without being marked as visited or cancelled.'
    )

    @api.depends('lead_id.city', 'partner_id.city', 'address')
    def _compute_city(self):
        for record in self:
            if not record.city:
                record.city = record.lead_id.city or record.partner_id.city or False

    @api.depends('state', 'date_booked')
    def _compute_is_overdue(self):
        now = fields.Datetime.now()
        for record in self:
            record.is_overdue = bool(
                record.state in ('open', 'rescheduled') and
                record.date_booked and
                record.date_booked < now
            )

    def _search_is_overdue(self, operator, value):
        now = fields.Datetime.now()
        is_true = (operator == '=' and value) or (operator == '!=' and not value)
        if is_true:
            return [
                ('state', 'in', ['open', 'rescheduled']),
                ('date_booked', '<', now)
            ]
        else:
            return [
                '|',
                ('state', 'not in', ['open', 'rescheduled']),
                ('date_booked', '>=', now)
            ]

    # --- Visit Execution & Outcome Fields (populated once visit occurs) ---
    actual_visitor_ids = fields.Many2many(
        'res.users',
        'crm_site_visit_actual_visitor_rel',
        'visit_id',
        'user_id',
        string='Persons Who Went',
        tracking=True,
        domain="[('share', '=', False), ('active', '=', True)]",
        help='Team members or representatives who physically attended the visit.'
    )
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

    @api.onchange('user_ids')
    def _onchange_user_ids(self):
        if self.user_ids and not self.user_id:
            self.user_id = self.user_ids[0]
        elif self.user_ids and self.user_id not in self.user_ids:
            self.user_id = self.user_ids[0]
        elif not self.user_ids:
            self.user_id = False

    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.user_id and self.user_id not in self.user_ids:
            self.user_ids = [(4, self.user_id.id)]

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
                if 'city' in fields_list and not res.get('city') and lead.city:
                    res['city'] = lead.city
                if 'address' in fields_list and not res.get('address'):
                    addr_parts = [p for p in [lead.street, lead.street2, lead.city] if p]
                    if addr_parts:
                        res['address'] = ', '.join(addr_parts)
        return res

    @api.onchange('lead_id')
    def _onchange_lead_id(self):
        if self.lead_id:
            if self.lead_id.partner_id:
                self.partner_id = self.lead_id.partner_id
            if self.lead_id.city and not self.city:
                self.city = self.lead_id.city
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
            # Synchronize user_ids and primary user_id
            if vals.get('user_id') and not vals.get('user_ids'):
                vals['user_ids'] = [(4, vals['user_id'])]
            # Default partner_id, city and address from lead if blank
            if vals.get('lead_id'):
                lead = self.env['crm.lead'].browse(vals['lead_id'])
                if lead.exists():
                    if not vals.get('partner_id') and lead.partner_id:
                        vals['partner_id'] = lead.partner_id.id
                    if not vals.get('city') and lead.city:
                        vals['city'] = lead.city
                    if not vals.get('address'):
                        addr_parts = [p for p in [lead.street, lead.street2, lead.city] if p]
                        if addr_parts:
                            vals['address'] = ', '.join(addr_parts)
        records = super().create(vals_list)
        for visit in records:
            if visit.lead_id:
                self.env.cr.execute(
                    "UPDATE crm_lead SET write_date = NOW() AT TIME ZONE 'UTC' WHERE id = %s",
                    (visit.lead_id.id,)
                )
                visit.lead_id.invalidate_recordset(['write_date'])
            if visit.lead_id and visit.date_booked and visit.state in ('open', 'rescheduled'):
                booked_date = fields.Datetime.to_datetime(visit.date_booked).date()
                lead = visit.lead_id
                if not lead.custom_next_contact_date or lead.custom_next_contact_date > booked_date:
                    lead.with_context(skip_ensure_activity=True).write({'custom_next_contact_date': booked_date})
        return records

    def write(self, vals):
        res = super().write(vals)
        leads = self.mapped('lead_id')
        if leads:
            self.env.cr.execute(
                "UPDATE crm_lead SET write_date = NOW() AT TIME ZONE 'UTC' WHERE id IN %s",
                (tuple(leads.ids),)
            )
            leads.invalidate_recordset(['write_date'])
        if 'date_booked' in vals or 'state' in vals:
            for visit in self:
                if visit.lead_id and visit.date_booked and visit.state in ('open', 'rescheduled'):
                    booked_date = fields.Datetime.to_datetime(visit.date_booked).date()
                    lead = visit.lead_id
                    if not lead.custom_next_contact_date or lead.custom_next_contact_date > booked_date:
                        lead.with_context(skip_ensure_activity=True).write({'custom_next_contact_date': booked_date})
        return res

    def action_mark_done(self):
        """Mark site visit as completed / visited."""
        for record in self:
            vals = {'state': 'done'}
            if not record.date_visited:
                vals['date_visited'] = fields.Datetime.now()
            if not record.actual_visitor_ids and record.user_ids:
                vals['actual_visitor_ids'] = [(6, 0, record.user_ids.ids)]
            if not record.actual_visitor_id:
                vals['actual_visitor_id'] = record.user_id or (record.user_ids[0] if record.user_ids else self.env.user)
            record.write(vals)
            visitors = ", ".join(record.actual_visitor_ids.mapped('name')) or record.actual_visitor_id.name or self.env.user.name
            record.message_post(
                body=_("Site visit marked as <b>Completed / Visited</b> by %s.") % (visitors,),
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
                'default_person_going_ids': [(6, 0, self.user_ids.ids)],
            }
        }

    @api.model
    def _cron_check_overdue_visits(self):
        """Monitors overdue site visits and schedules warning activities for assigned users."""
        now = fields.Datetime.now()
        overdue_visits = self.search([
            ('state', 'in', ['open', 'rescheduled']),
            ('date_booked', '<', now)
        ])
        todo_activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        activity_type_id = todo_activity_type.id if todo_activity_type else False

        for visit in overdue_visits:
            attendees = visit.user_ids or visit.user_id
            for user in attendees:
                existing = visit.activity_ids.filtered(
                    lambda a: 'Overdue Site Visit' in (a.summary or '') and a.user_id == user
                )
                if not existing:
                    try:
                        visit.activity_schedule(
                            activity_type_id=activity_type_id or self.env.ref('mail.mail_activity_data_warning').id,
                            summary=_('Overdue Site Visit: %s') % (visit.name,),
                            note=_(
                                'This site visit scheduled for %s has passed its scheduled date and has not been marked as visited or rescheduled. '
                                'Please visit the site, record visit details, or reschedule.'
                            ) % (visit.date_booked,),
                            user_id=user.id,
                            date_deadline=fields.Date.context_today(visit),
                        )
                    except Exception:
                        pass
        return True
