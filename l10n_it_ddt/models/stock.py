# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Apulia Software s.r.l. (http://www.apuliasoftware.it)
#    @author Francesco Apruzzese <f.apruzzese@apuliasoftware.it>
#    Copyright 2015 Lorenzo Battistini - Agile Business Group
#
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
##############################################################################


from openerp import fields, models, api


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    ddt_ids = fields.Many2many(
        comodel_name='stock.picking.package.preparation',
        relation='stock_picking_pack_prepare_rel',
        column1='stock_picking_id',
        column2='stock_picking_package_preparation_id',
        string='DdT',
        copy=False, )

    has_ddt = fields.Boolean(
        string="Has DdT?",
        readonly=True,
        compute='_compute_has_ddt'
    )

    @api.multi
    @api.depends('ddt_ids')
    def _compute_has_ddt(self):
        """True if any DdT is assigned to the picking."""
        for item in self:
            item.has_ddt = bool(item.ddt_ids)

    @api.multi
    def write(self, values):
        pack_to_update = None
        if 'move_lines' in values:
            pack_to_update = self.env['stock.picking.package.preparation']
            for picking in self:
                pack_to_update |= picking.ddt_ids
        res = super(StockPicking, self).write(values)
        if pack_to_update:
            pack_to_update._update_line_ids()
        return res

    @api.multi
    def unlink(self):
        pack_to_update = self.env['stock.picking.package.preparation']
        for picking in self:
            pack_to_update |= picking.ddt_ids
        res = super(StockPicking, self).unlink()
        if pack_to_update:
            pack_to_update._update_line_ids()
        return res

    @api.model
    def create(self, values):
        picking = super(StockPicking, self).create(values)
        if picking.ddt_ids:
            picking.ddt_ids._update_line_ids()
        return picking

    @api.multi
    def open_related_ddt(self):
        """Action to open tree view of the sections of the committee."""
        self.ensure_one()
        domain = [
            ('id', '=', self.ddt_ids.ids),
        ]
        return {
            'name': 'DdT',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking.package.preparation',
            'target': 'current',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': domain,
        }