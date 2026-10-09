# -*- coding: utf-8 -*-
{
    'name': 'CRM Site Visits',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Schedule, track, and manage client site visits and reschedules from CRM leads.',
    'description': """
CRM Site Visits Management
===========================
* Book and track client site visits directly from CRM leads.
* Record visitor assigned, date booked, site address, and outcome.
* Audit and manage client reschedule requests.
* Calendar, list, and form views with quick status transitions.
    """,
    'author': 'Showline Solutions',
    'license': 'LGPL-3',
    'depends': ['crm', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/crm_site_visit_sequence.xml',
        'data/crm_site_visit_cron.xml',
        'wizard/crm_site_visit_reschedule_wizard_views.xml',
        'views/crm_site_visit_views.xml',
        'views/crm_lead_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'crm_site_visit/static/src/views/**/*',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
