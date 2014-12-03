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


@api.model
def _get_models(self):
    models = self.env.user.company_id.advance_model_ids
    return [(model.model, model.display_name) for model in models]


class AccountAdvance(models.Model):

    _name = 'account.advance'
    _description = 'Advance Payment'

    name = fields.Reference(_get_models, string='Referenced Item')


class AccountVoucher(models.Model):

    _inherit = 'account.voucher'

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

    ref_id = fields.Reference(_get_models, string='Referenced Item')
    ref_ids = fields.Many2many('account.advance', string='Test')
    advance_account_id = fields.Many2one(
        'account.account',
        string='Advance Account')

    @api.onchange('ref_id')
    def onchange_ref_id(self):
        model_obj = self.env['ir.model']
        if self.ref_id:
            ir_model = self.ref_id._model
            model = model_obj.search([('model', '=', ir_model._name)])
            name = "%s %s" % (model.name, self.ref_id.name)
            self.name = name

    def action_move_line_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        res = super(AccountVoucher, self).action_move_line_create(
            cr, uid, ids, context)

        for voucher in self.browse(cr, uid, ids, context=context):
            for line in voucher.move_id.line_id:
                line.ref_id = voucher.ref_id
                if voucher.advance_account_id and line.account_id != \
                        voucher.account_id:
                    line.account_id = voucher.advance_account_id.id

        return res


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    ref_id = fields.Reference(_get_models, string='Referenced Item')


class AccountBankStatementLine(models.Model):

    _inherit = 'account.bank.statement.line'

    ref_id = fields.Reference(_get_models, string='Referenced Item')

    def process_reconciliation(self, cr, uid, id, mv_line_dicts, context=None):

        if not context:
            context = {}

        st_line = self.browse(cr, uid, id)
        for line in mv_line_dicts:
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

        res['ref_id'] = '%s,%s' % (
            st_line.ref_id._model, str(st_line.ref_id.id))

        return res
