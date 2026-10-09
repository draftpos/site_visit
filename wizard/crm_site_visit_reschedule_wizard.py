# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CrmSiteVisitRescheduleWizard(models.TransientModel):
    _name = 'crm.site.visit.reschedule.wizard'
    _description = 'Reschedule CRM Site Visit Wizard'

    visit_id = fields.Many2one('crm.site.visit', string='Site Visit', required=True, readonly=True)
    current_date = fields.Datetime(related='visit_id.date_booked', string='Current Scheduled Date', readonly=True)
    new_date = fields.Datetime(string='New Scheduled Date', required=True)
    person_going_id = fields.Many2one(
        'res.users',
        string='Person Going',
        domain="[('share', '=', False), ('active', '=', True)]"
    )
    reason = fields.Text(
        string='Reason for Rescheduling',
        required=True,
        help='Detail why the appointment was rescheduled.'
    )

    def action_confirm_reschedule(self):
        self.ensure_one()
        visit = self.visit_id
        old_date_str = fields.Datetime.to_string(visit.date_booked)
        new_date_str = fields.Datetime.to_string(self.new_date)
        
        vals = {
            'date_booked': self.new_date,
            'state': 'rescheduled',
            'reschedule_count': visit.reschedule_count + 1,
            'reschedule_reason': self.reason,
        }
        if self.person_going_id:
            vals['user_id'] = self.person_going_id.id
            
        visit.write(vals)
        
        # Log audit trail to chatter
        msg = _(
            "<b>Site Visit Rescheduled (Reschedule #%d)</b><br/>"
            "<b>Previous Date:</b> %s<br/>"
            "<b>New Date:</b> %s<br/>"
            "<b>Person Going:</b> %s<br/>"
            "<b>Reason:</b> %s"
        ) % (
            visit.reschedule_count,
            old_date_str,
            new_date_str,
            (self.person_going_id or visit.user_id).name,
            self.reason
        )
        visit.message_post(body=msg, subtype_xmlid='mail.mt_note')
        visit.lead_id.message_post(body=msg, subtype_xmlid='mail.mt_note')
        
        return {'type': 'ir.actions.act_window_close'}
