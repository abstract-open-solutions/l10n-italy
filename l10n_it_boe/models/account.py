# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Abstract (http://www.abstract.it)
#    Author: Davide Corio <davide.corio@abstract.it>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    boe_doc_type = fields.Selection(
        [
            ('supplier_invoice', 'Supplier Invoice'),
            ('forwarder_invoice', 'Forwarder Invoice')],
        'Customs Document Type', readonly=True)

    @api.multi
    def action_move_create(self):
        res = super(AccountInvoice, self).action_move_create()
        company = self.env.user.company_id
        if self.boe_doc_type and self.boe_doc_type == 'supplier_invoice':
            self.move_id.button_cancel()
            for line in self.move_id.line_id:
                tot_debit = 0
                if line.debit:
                    tot_debit += line.debit

            for line in self.move_id.line_id:
                if line.credit:
                    orig_credit = line.credit
                    line.credit = line.credit - (line.credit - tot_debit)
                    supplier_line = line.copy()
                    supplier_line.account_id = company.boe_account_id.id
                    supplier_line.partner_id = company.boe_partner_id.id
                    supplier_line.credit = orig_credit - tot_debit
        return res
