# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Apulia Software s.r.l. (http://www.apuliasoftware.it)
#    @author Francesco Apruzzese <f.apruzzese@apuliasoftware.it>
#
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
##############################################################################


from openerp import models, fields, api, exceptions, _


class StockPickingCarriageCondition(models.Model):

    _name = "stock.picking.carriage_condition"
    _description = "Carriage Condition"

    name = fields.Char(string='Carriage Condition', required=True)
    note = fields.Text(string='Note')


class StockPickingGoodsDescription(models.Model):

    _name = 'stock.picking.goods_description'
    _description = "Description of Goods"

    name = fields.Char(string='Description of Goods', required=True)
    note = fields.Text(string='Note')


class StockPickingTransportationReason(models.Model):

    _name = 'stock.picking.transportation_reason'
    _description = 'Reason for Transportation'

    name = fields.Char(string='Reason For Transportation', required=True)
    note = fields.Text(string='Note')


class StockPickingTransportationMethod(models.Model):

    _name = 'stock.picking.transportation_method'
    _description = 'Method of Transportation'

    name = fields.Char(string='Method of Transportation', required=True)
    note = fields.Text(string='Note')


class StockDdtType(models.Model):

    _name = 'stock.ddt.type'
    _description = 'Stock DdT Type'
    _inherit = ['mail.thread']

    name = fields.Char(required=True)
    sequence_id = fields.Many2one('ir.sequence', required=True)
    note = fields.Text(string='Note')


class StockPickingPackagePreparation(models.Model):

    _inherit = 'stock.picking.package.preparation'
    _rec_name = 'display_name'

    def _default_ddt_type(self):
        return self.env['stock.ddt.type'].search([], limit=1)

    ddt_type_id = fields.Many2one(
        'stock.ddt.type', string='DdT Type', default=_default_ddt_type)
    ddt_number = fields.Char(string='DdT Number')
    partner_invoice_id = fields.Many2one('res.partner')
    partner_shipping_id = fields.Many2one('res.partner')
    carriage_condition_id = fields.Many2one(
        'stock.picking.carriage_condition', 'Carriage Condition')
    goods_description_id = fields.Many2one(
        'stock.picking.goods_description', 'Description of Goods')
    transportation_reason_id = fields.Many2one(
        'stock.picking.transportation_reason',
        'Reason for Transportation')
    transportation_method_id = fields.Many2one(
        'stock.picking.transportation_method',
        'Method of Transportation')
    carrier_id = fields.Many2one(
        'res.partner', string='Carrier')
    parcels = fields.Integer()
    display_name = fields.Char(string='Name', compute='_compute_display_name')
    volume = fields.Float('Volume')
    invoice_id = fields.Many2one(
        'account.invoice', string="Invoice", readonly=True)

    @api.onchange('partner_id', 'ddt_type_id')
    def on_change_partner(self):
        if self.ddt_type_id:
            addr = self.partner_id.address_get(['delivery', 'invoice'])
            self.partner_invoice_id = addr['invoice']
            self.partner_shipping_id = addr['delivery']
            self.carriage_condition_id = \
                self.partner_id.carriage_condition_id.id \
                if self.partner_id.carriage_condition_id else False
            self.goods_description_id = \
                self.partner_id.goods_description_id.id \
                if self.partner_id.goods_description_id else False
            self.transportation_reason_id = \
                self.partner_id.transportation_reason_id.id \
                if self.partner_id.transportation_reason_id else False
            self.transportation_method_id = \
                self.partner_id.transportation_method_id.id \
                if self.partner_id.transportation_method_id else False

    @api.multi
    def action_put_in_pack(self):
        for package in self:
            # ----- Assign ddt number if ddt type is set
            if package.ddt_type_id and not package.ddt_number:
                package.ddt_number = package.ddt_type_id.sequence_id.get(
                    package.ddt_type_id.sequence_id.code)
        return super(StockPickingPackagePreparation, self).action_put_in_pack()

    @api.multi
    def set_done(self):
        for picking in self.picking_ids:
            if picking.state != 'done':
                raise exceptions.Warning(
                    _("Not every picking is in done status"))
        for package in self:
            if not package.ddt_number:
                package.ddt_number = package.ddt_type_id.sequence_id.get(
                    package.ddt_type_id.sequence_id.code)
        self.write({'state': 'done', 'date_done': fields.Datetime.now()})
        return True

    @api.one
    @api.depends('name', 'ddt_number', 'partner_id', 'date')
    def _compute_display_name(self):
        name = u''
        if self.name:
            name = self.name
        if self.ddt_number and self.name:
            name = u'[{package}] {ddt}'.format(package=self.name,
                                               ddt=self.ddt_number)
        if self.ddt_number and not self.name:
            name = self.ddt_number
        if not name:
            name = u'{partner} of {date}'.format(partner=self.partner_id.name,
                                                 date=self.date)
        self.display_name = name


class StockPickingPackagePreparationLine(models.Model):

    _inherit = 'stock.picking.package.preparation.line'

    invoiceable = fields.Selection(
        [('none', 'None'), ('invoiceable', 'Invoiceable')],
        default='invoiceable')

    @api.multi
    def get_move_data(self):
        move_data = super(StockPickingPackagePreparationLine,
                          self).get_move_data()
        if self.invoiceable == 'invoiceable':
            move_data.update({
                'invoice_state': '2binvoiced',
                })
        return move_data
