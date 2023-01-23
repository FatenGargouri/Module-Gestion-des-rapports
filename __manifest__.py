# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Rapports',
    'version': '1.1',
    'category': 'Human Resources/Rapports',
    'sequence': 95,
    'summary': 'Rapports',
    'description': "",
    'depends': [
        'base',
        'mail',
        'hr',



    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/form_journalier_views.xml',
        'views/template_rapport_journalier_views.xml',
        'views/rapport_journalier_views.xml',
        'views/form_synthese_views.xml',
        'views/template_rapport_synthese_views.xml',
        'views/rapport_synthese_views.xml',
        'views/menu.xml',






    ],
    'demo': [

    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {


    },
    'license': 'LGPL-3',
}