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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning


@api.model
def _get_models(self):
    models = self.env.user.company_id.advance_model_ids
    return [(model.model, model.display_name) for model in models]


class AccountAdvance(models.Model):

    _name = 'account.advance'
    _description = 'Advance Payment'

    @api.one
    def _get_ref_name(self):
        if self.ref_id:
            self.name = self.ref_id.name

    @api.one
    def _get_ref_model(self):
        if self.ref_id:
            self.ref_model = self.ref_id._model

    ref_id = fields.Reference(_get_models, string='Referenced Item')
    name = fields.Char(string='Name', compute='_get_ref_name')
    voucher_id = fields.Many2one('account.voucher', 'Voucher')
    amount = fields.Float('Amount', digits=dp.get_precision('Account'))


class AccountVoucher(models.Model):

    _inherit = 'account.voucher'

    @api.onchange('advanced_amount')
    def onchange_advance_amount(self):
        if self.advanced_amount > self.writeoff_amount:
            raise Warning(
                _('Impossible to allocate %s, since the difference amount is \
%s') % (
                    self.advanced_amount,
                    self.writeoff_amount))

    @api.model
    def _get_advance_account(self):
        voucher_type = self.env.context.get('type', False)
        company = self.env.user.company_id

        if voucher_type == 'receipt':
            advance_account_id = company.received_advance_account_id.id
        elif voucher_type == 'payment':
            advance_account_id = company.issued_advance_account_id.id
        else:
            advance_account_id = False

        return advance_account_id

    @api.model
    def _get_advanced_amount(self):
        amount = 0
        for advance in self.ref_ids:
            amount += advance.amount
        self.advanced_amount = amount

    ref_id = fields.Reference(_get_models, string='Referenced Item')
    ref_ids = fields.One2many(
        'account.advance', 'voucher_id', string='Related Items')
    advance_account_id = fields.Many2one(
        'account.account',
        string='Advance Account')
    advanced_amount = fields.Float(
        'Advanced Amount',
        digits=dp.get_precision('Account'),
        compute='_get_advanced_amount')

    @api.onchange('ref_id')
    def onchange_ref_id(self):
        model_obj = self.env['ir.model']
        if self.ref_id:
            ir_model = self.ref_id._model
            model = model_obj.search([('model', '=', ir_model._name)])
            name = "%s %s" % (model.name, self.ref_id.name)
            self.name = name

    @api.onchange('ref_ids')
    def onchange_ref_ids(self):
        amount = 0
        for advance in self.ref_ids:
            amount += advance.amount
        self.advanced_amount = amount

    def action_move_line_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        move_model = self.pool['account.move.line']
        res = super(AccountVoucher, self).action_move_line_create(
            cr, uid, ids, context)

        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.ref_ids:
                for line in voucher.move_id.line_id:
                    if not line.reconcile_id\
                            and line.credit == voucher.writeoff_amount:
                        for ref in voucher.ref_ids:
                            new_line = line.copy()
                            if voucher.type == 'receipt':
                                new_line.credit = ref.amount
                            elif voucher.type == 'payment':
                                new_line.debit = ref.amount
                            new_line.ref_id = ref.ref_id
                            new_line.advance_id = ref
                        move_model.unlink(cr, uid, line.id)
        return res


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    ref_id = fields.Reference(_get_models, string='Referenced Item')
    advance_id = fields.Many2one('account.advance', 'Advance Payment')


class AccountBankStatementLine(models.Model):

    _inherit = 'account.bank.statement.line'

    ref_id = fields.Reference(_get_models, string='Referenced Item')
    advance_id = fields.Many2one('account.advance', 'Advance Payment')

    def process_reconciliation(self, cr, uid, id, mv_line_dicts, context=None):

        if not context:
            context = {}

        st_line = self.browse(cr, uid, id)
        for line in mv_line_dicts:
            if st_line.ref_id:
                line['ref_id'] = '%s,%s' % (
                    st_line.ref_id._model, str(st_line.ref_id.id))

        return super(AccountBankStatementLine, self).process_reconciliation(
            cr, uid, id, mv_line_dicts, context=None)


class AccountBankStatement(models.Model):

    _inherit = 'account.bank.statement'

    def _prepare_move_line_vals(
        self, cr, uid, st_line, move_id, debit, credit, currency_id=False,
            amount_currency=False, account_id=False, partner_id=False,
            context=None):

        if not context:
            context = {}

        res = super(AccountBankStatement, self)._prepare_move_line_vals(
            cr, uid, st_line, move_id, debit, credit, currency_id=currency_id,
            amount_currency=amount_currency, account_id=account_id,
            partner_id=partner_id, context=context)

        if st_line.ref_id:
            res['ref_id'] = '%s,%s' % (
                st_line.ref_id._model, str(st_line.ref_id.id))

        return res
