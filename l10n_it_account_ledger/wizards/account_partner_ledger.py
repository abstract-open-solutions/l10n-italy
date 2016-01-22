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

from openerp import models, fields


class AccountPartnerLedger(models.TransientModel):

    _inherit = 'account.partner.ledger'

    include_journal = fields.Boolean('Include Journal')
    include_account = fields.Boolean('Include Account')
    include_counterparts = fields.Boolean('Include Counterparts')
    include_entry_name = fields.Boolean('Include Entry Name')
    include_row_number = fields.Boolean('Include Row Number')
    include_supplier_invoice = fields.Boolean('Include Supplier Invoice')

    def _print_report(self, cr, uid, ids, data, context=None):
        filters = [
            'include_journal',
            'include_account',
            'include_counterparts',
            'include_row_number',
            'include_entry_name',
            'include_supplier_invoice']
        data['form'].update(self.read(cr, uid, ids, filters)[0])
        return super(AccountPartnerLedger, self)._print_report(
            cr, uid, ids, data, context)
