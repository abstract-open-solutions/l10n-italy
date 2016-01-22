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

from openerp.addons.account.report import account_partner_ledger
from openerp.osv import osv


class ThirdPartyLedger(account_partner_ledger.third_party_ledger):

    def __init__(self, cr, uid, name, context=None):
        super(ThirdPartyLedger, self).__init__(
            cr, uid, name, context=context)

        self.localcontext.update({
            'display_counterparts': self._display_counterparts,
            'display_supplier_invoice': self._display_supplier_invoice,
            'include_account': self._include_account,
            'include_journal': self._include_journal,
            'include_counterparts': self._include_counterparts,
            'include_entry_name': self._include_entry_name,
            'include_supplier_invoice': self._include_supplier_invoice,
            'get_colspan': self._get_colspan,
            'include_row_number': self._include_row_number,
            'colspan': self._get_colspan,
            'debug': self._debug,
            'get_partner_name': self._get_partner_name,
            })

    def _debug(self, arg):
        import ipdb;ipdb.set_trace()

    def _get_partner_name(self):
        partner_model = self.pool['res.partner']
        names = []
        partner_ids = self.localcontext['active_ids']
        for partner_id in partner_ids:
            partner = partner_model.browse(self.cr, self.uid, partner_id)
            names.append(partner.name)
        if names:
            return ', '.join(names)
        else:
            return ''

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

    def _include_account(self):
        if self.localcontext['data']['form']['include_account']:
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
        if self.localcontext['data']['form']['include_account']:
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
        line = line_model.browse(self.cr, self.uid, line['id'])
        codes = ["%s - %s" % (l.account_id.code, l.account_id.name) for l in
                 line.move_id.line_id if l.account_id != line.account_id]
        return ', '.join(set(codes))

    def _display_supplier_invoice(self, line):
        line_model = self.pool['account.move.line']
        invoice_model = self.pool['account.invoice']
        line = line_model.browse(self.cr, self.uid, line['id'])
        invoice_id = invoice_model.search(
            self.cr, self.uid, [('move_id', '=', line.move_id.id)])
        if invoice_id:
            invoice = invoice_model.browse(self.cr, self.uid, invoice_id)
            return invoice.supplier_invoice_number or ''
        else:
            return ''


class report_partnerledger(osv.AbstractModel):
    _inherit = 'report.account.report_partnerledger'
    _wrapped_report_class = ThirdPartyLedger
