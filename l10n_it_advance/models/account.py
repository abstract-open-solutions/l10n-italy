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


class AccountVoucher(models.Model):

    _inherit = 'account.voucher'

    ref_id = fields.Reference(_get_models, string='Referenced Item')

    @api.onchange('ref_id')
    def onchange_ref_id(self):
        model_obj = self.env['ir.model']
        if self.ref_id:
            ir_model = self.ref_id._model
            model = model_obj.search([('model', '=', ir_model._name)])
            name = "%s %s" % (model.name, self.ref_id.name)
            self.name = name


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    ref_id = fields.Reference(_get_models, string='Referenced Item')


class AccountBankStatementLine(models.Model):

    _inherit = 'account.bank.statement.line'

    ref_id = fields.Reference(_get_models, string='Referenced Item')
