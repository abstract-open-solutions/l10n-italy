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
        [('supplier_invoice', 'Supplier Invoice'),
            ('forwarder_invoice', 'Forwarder Invoice')],
        'Customs Document Type', readonly=True)
    forwarder_boe_invoice_id = fields.Many2one(
        'account.invoice',
        string='Forwarder Invoice (BoE)',
        copy=False)

    supplier_boe_invoice_id = fields.Many2one(
        'account.invoice',
        string='Supplier Invoice (BoE)',
        copy=False)

    @api.multi
    def action_move_create(self):
        res = super(AccountInvoice, self).action_move_create()
        company = self.env.user.company_id
        boe_accounts = company.boe_cost_account_ids
        if self.boe_doc_type and self.boe_doc_type == 'supplier_invoice':
            tot_debit = 0
            for line in self.move_id.line_id:
                if line.account_id in boe_accounts:
                    tot_debit += line.debit
            for line in self.move_id.line_id:
                if line.credit:
                    orig_credit = line.credit
                    line.write(
                        {'credit': line.credit - tot_debit},
                        update_check=False)
                    supplier_line = line.copy()
                    supplier_line.write(
                        {'account_id': company.boe_account_id.id},
                        update_check=False)
                    supplier_line.write(
                        {'partner_id': self.partner_id.id},
                        update_check=False)
                    supplier_line.write(
                        {'credit': tot_debit},
                        update_check=False)
                    rate = self.custom_exchange_rate
                    if self.currency_id != self.company_id.currency_id:
                        supp_amount_currency = line.currency_id.with_context(
                            custom_exchange_rate=1/rate).compute(
                            orig_credit - tot_debit,
                            line.company_id.currency_id)
                        supplier_line.write(
                            {'amount_currency': -(supp_amount_currency)},
                            update_check=False)
                        line_amount_currency = line.currency_id.with_context(
                            custom_exchange_rate=1/rate).compute(
                            line.credit - (line.credit - tot_debit),
                            line.company_id.currency_id)
                        line.write(
                            {'amount_currency': -(line_amount_currency)},
                            update_check=False)

        return res

    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        if vals.get('supplier_boe_invoice_id', False):
            supplier_boe_invoice = self.browse(
                vals.get('supplier_boe_invoice_id'))
            if not supplier_boe_invoice.forwarder_boe_invoice_id:
                supplier_boe_invoice.forwarder_boe_invoice_id = self.id

        if vals.get('forwarder_boe_invoice_id', False):
            forwarder_boe_invoice = self.browse(
                vals.get('forwarder_boe_invoice_id'))
            if not forwarder_boe_invoice.supplier_boe_invoice_id:
                forwarder_boe_invoice.supplier_boe_invoice_id = self.id
        return res
