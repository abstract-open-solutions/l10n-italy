# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Abstract (http://www.abstract.it)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Account Ledger',
    'version': '1.2',
    'category': 'Localization/Italy',
    'summary': 'Account Ledger',
    'author': 'Davide Corio, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': ['account', 'l10n_it_account'],
    'data': [
        'views/account_general_ledger_view.xml',
        'views/account_partner_ledger_view.xml',
        'views/account_partner_ledgerother_view.xml',
        'wizards/account_partner_ledger_view.xml',
        'wizards/account_general_ledger_view.xml',
        'paperformat.xml',
    ],
    'test': [],
    'installable': True,
}
