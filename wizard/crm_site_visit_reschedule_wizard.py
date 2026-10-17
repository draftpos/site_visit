# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CrmSiteVisitRescheduleWizard(models.TransientModel):
    _name = 'crm.site.visit.reschedule.wizard'
    _description = 'Reschedule CRM Site Visit Wizard'

    visit_id = fields.Many2one('crm.site.visit', string='Site Visit', required=True, readonly=True)
    current_date = fields.Datetime(related='visit_id.date_booked', string='Current Scheduled Date', readonly=True)
    new_date = fields.Datetime(string='New Scheduled Date', required=True)
    person_going_ids = fields.Many2many(
        'res.users',
        string='Persons Going',
        domain="[('share', '=', False), ('active', '=', True)]",
        help='Representatives scheduled to attend the visit.'
    )
    person_going_id = fields.Many2one(
        'res.users',
        string='Primary Person Going',
        domain="[('share', '=', False), ('active', '=', True)]"
    )
    reason = fields.Text(
        string='Reason for Rescheduling',
        required=True,
        help='Detail why the appointment was rescheduled.'
    )

    @api.onchange('person_going_ids')
    def _onchange_person_going_ids(self):
        if self.person_going_ids and not self.person_going_id:
            self.person_going_id = self.person_going_ids[0]
        elif self.person_going_ids and self.person_going_id not in self.person_going_ids:
            self.person_going_id = self.person_going_ids[0]
        elif not self.person_going_ids:
            self.person_going_id = False

    @api.onchange('person_going_id')
    def _onchange_person_going_id(self):
        if self.person_going_id and self.person_going_id not in self.person_going_ids:
            self.person_going_ids = [(4, self.person_going_id.id)]

    def action_confirm_reschedule(self):
        self.ensure_one()
        visit = self.visit_id
        old_date_str = fields.Datetime.to_string(visit.date_booked)
        new_date_str = fields.Datetime.to_string(self.new_date)
        
        vals = {
            'date_booked': self.new_date,
            'state': 'rescheduled',
            'date_rescheduled': fields.Datetime.now(),
            'reschedule_count': visit.reschedule_count + 1,
            'reschedule_reason': self.reason,
        }
        if self.person_going_ids:
            vals['user_ids'] = [(6, 0, self.person_going_ids.ids)]
            vals['user_id'] = self.person_going_id.id if self.person_going_id else self.person_going_ids[0].id
        elif self.person_going_id:
            vals['user_id'] = self.person_going_id.id
            vals['user_ids'] = [(4, self.person_going_id.id)]
            
        visit.write(vals)
        
        # Log audit trail to chatter
        attendees = ", ".join(visit.user_ids.mapped('name')) or (self.person_going_id or visit.user_id).name
        msg = _(
            "<b>Site Visit Rescheduled (Reschedule #%d)</b><br/>"
            "<b>Previous Date:</b> %s<br/>"
            "<b>New Date:</b> %s<br/>"
            "<b>Persons Going:</b> %s<br/>"
            "<b>Reason:</b> %s"
        ) % (
            visit.reschedule_count,
            old_date_str,
            new_date_str,
            attendees,
            self.reason
        )
        visit.message_post(body=msg, subtype_xmlid='mail.mt_note')
        visit.lead_id.message_post(body=msg, subtype_xmlid='mail.mt_note')
        
        return {'type': 'ir.actions.act_window_close'}
