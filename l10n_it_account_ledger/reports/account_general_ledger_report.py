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

from collections import OrderedDict

from openerp.addons.account.report import account_general_ledger
from openerp.osv import osv
from openerp.exceptions import Warning
from openerp import _


class GeneralLedger(account_general_ledger.general_ledger):

    def __init__(self, cr, uid, name, context=None):
        super(GeneralLedger, self).__init__(
            cr, uid, name, context=context)

        self.localcontext.update({
            'display_counterparts': self._display_counterparts,
            'display_supplier_invoice': self._display_supplier_invoice,
            'include_journal': self._include_journal,
            'include_counterparts': self._include_counterparts,
            'include_entry_name': self._include_entry_name,
            'include_supplier_invoice': self._include_supplier_invoice,
            'include_initial_balance': self._include_initial_balance,
            'get_colspan': self._get_colspan,
            # 'get_final_balance': self._get_final_balance,
            'include_row_number': self._include_row_number,
            'colspan': self._get_colspan,
            'debug': self._debug,
            # 'get_partner_name': self._get_partner_name,
            })

    def _debug(self, arg):
        import pdb;pdb.set_trace()

    # def lines(self, account):
    #     """ this override will group all the account_move_lines by move_name
    #     """
    #     lines = super(GeneralLedger, self).lines(account)
    #     if not lines:
    #         return lines
    #     lines_groups = OrderedDict()
    #     for l in lines:
    #         move_name = l['move_name']
    #         if move_name in lines_groups:
    #             old_line = lines_groups[move_name]
    #             l['debit'] += old_line['debit']
    #             l['credit'] += old_line['credit']
    #         lines_groups[move_name] = l
    #     new_res = lines_groups.values()
    #     # ...and now we have to update the progresses
    #     sum = 0.0
    #     if self.init_balance:
    #         sum = self.init_bal_sum
    #     for r in new_res:
    #         sum += r['debit'] - r['credit']
    #         r['progress'] = sum
    #     return new_res

    def _include_initial_balance(self):
        if self.localcontext['data']['form']['initial_balance']:
            return True
        return False

    # def _get_partner_name(self):
    #     partner_model = self.pool['res.partner']
    #     names = []
    #     partner_ids = self.localcontext['active_ids']
    #     for partner_id in partner_ids:
    #         partner = partner_model.browse(self.cr, self.uid, partner_id)
    #         names.append(partner.name)
    #     if names:
    #         return ', '.join(names)
    #     else:
    #         return ''

    def _include_journal(self):
        if self.localcontext['data']['form']['include_journal']:
            return True
        return False

    def _include_supplier_invoice(self):
        if self.localcontext['data']['form']['include_supplier_invoice']:
            return True
        return False

    def _include_row_number(self):
        if self.localcontext['data']['form']['include_row_number']:
            return True
        return False

    def _include_counterparts(self):
        if self.localcontext['data']['form']['include_counterparts']:
            return True
        return False

    def _include_entry_name(self):
        if self.localcontext['data']['form']['include_entry_name']:
            return True
        return False

    def _get_colspan(self):
        colspan = 2
        if self.localcontext['data']['form']['include_entry_name']:
            colspan += 1
        if self.localcontext['data']['form']['include_counterparts']:
            colspan += 1
        if self.localcontext['data']['form']['include_journal']:
            colspan += 1
        if self.localcontext['data']['form']['include_row_number']:
            colspan += 1
        if self.localcontext['data']['form']['include_supplier_invoice']:
            colspan += 1
        return colspan

    def _display_counterparts(self, line):
        line_model = self.pool['account.move.line']
        line = line_model.browse(self.cr, self.uid, line['lid'])
        codes = ["%s - %s" % (l.account_id.code, l.account_id.name) for l in
                 line.move_id.line_id if l.account_id != line.account_id]
        return ', '.join(set(codes))

    def _display_supplier_invoice(self, line):
        line_model = self.pool['account.move.line']
        invoice_model = self.pool['account.invoice']
        line = line_model.browse(self.cr, self.uid, line['lid'])
        invoice_id = invoice_model.search(
            self.cr, self.uid, [('move_id', '=', line.move_id.id)])
        if invoice_id:
            invoice = invoice_model.browse(self.cr, self.uid, invoice_id)
            return invoice.supplier_invoice_number or ''
        else:
            return ''


class report_generalledger(osv.AbstractModel):
    _inherit = 'report.account.report_generalledger'
    _wrapped_report_class = GeneralLedger
