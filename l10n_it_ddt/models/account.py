# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Abstract (http://www.abstract.it)
#    @author Davide Corio <davide.corio@abstract.it>
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


from openerp import fields, model, api


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    carriage_condition_id = fields.Many2one(
        'stock.picking.carriage_condition', string='Carriage Condition')
    goods_description_id = fields.Many2one(
        'stock.picking.goods_description', string='Description of Goods')
    transportation_reason_id = fields.Many2one(
        'stock.picking.transportation_reason',
        string='Reason for Transportation')
    transportation_method_id = fields.Many2one(
        'stock.picking.transportation_method',
        string='Method of Transportation')
    parcels = fields.integer('Number of Packages')

    def onchange_partner_id(
            self, type, partner_id, date_invoice=False, payment_term=False,
            partner_bank_id=False, company_id=False):
        result = super(AccountInvoice, self).onchange_partner_id(
            type, partner_id, date_invoice, payment_term, partner_bank_id,
            company_id)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            for k in ('carriage_condition_id',
                      'goods_description_id',
                      'transportation_reason_id',
                      'transportation_method_id'):
                value = getattr(partner, k)
                result['value'][k] = value.id
        return result
