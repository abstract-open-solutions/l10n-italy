# -*- coding: utf-8 -*-
# Copyright 2012 Associazione OpenERP Italia (<http://www.openerp-italia.org>).
# Copyright 2016 Davide Corio (Abstract)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.exceptions import ValidationError


class IrSequenceDateRange(models.Model):
    _inherit = 'ir.sequence.date_range'

    def _next(self):
        invoice_model = self.env['account.invoice']
        number = super(IrSequenceDateRange, self)._next()
        invoice = self._context.get('invoice', False)
        inv_type = invoice.type
        if inv_type == 'out_invoice' or inv_type == 'out_refund':
            date_invoice = invoice.date_invoice
            journal = invoice.journal_id.id
            res = invoice_model.search([
                ('type', '=', inv_type),
                ('date_invoice', '>', date_invoice),
                ('number', '<', number),
                ('journal_id', '=', journal)])
            if res:
                raise ValidationError(
                    _('Cannot create invoice! Post the invoice with a\
                        greater date'))
        return number
