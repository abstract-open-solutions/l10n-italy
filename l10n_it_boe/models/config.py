# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Abstract (http://www.abstract.it)
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

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    boe_account_id = fields.Many2one(
        'account.account',
        string='Bill of Entry Account')
    boe_partner_id = fields.Many2one(
        'res.partner',
        string='Customs Partner')


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    boe_account_id = fields.Many2one(
        'account.account',
        string='Customs Account',
        related='company_id.boe_account_id')
    boe_partner_id = fields.Many2one(
        'res.partner',
        string='Customs Partner',
        related='company_id.boe_partner_id')

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        res = super(AccountConfigSettings, self).onchange_company_id(
            cr, uid, ids, company_id, context=context)
        if company_id:
            company = self.pool.get('res.company').browse(
                cr, uid, company_id, context=context)
            res['value'].update({
                'boe_account_id': company.boe_account_id,
                'boe_partner_id': company.boe_partner_id,
                })
        else:
            res['value'].update({
                'boe_account_id': False,
                'boe_partner_id': False,
                })
        return res
