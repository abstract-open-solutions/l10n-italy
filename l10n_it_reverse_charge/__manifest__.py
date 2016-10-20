# -*- coding: utf-8 -*-
# © 2016 Davide Corio (Abstract)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Reverse Charge',
    'version': '10.0.1.0.0',
    'summary': 'Reverse Charge for Italy',
    'author': 'Odoo Italia Network,Odoo Community Association (OCA)',
    'website': 'http://www.odoo-community.org',
    'depends': [
        'account', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'data/rc_type.xml',
        'views/account_view.xml',
    ],
    'demo': ['demo/reverse_charge_demo.yml'],
    'installable': True,
}
