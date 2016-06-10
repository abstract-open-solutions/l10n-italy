# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Simone Orsi <simone.orsi@abstract.it>
#    Copyright (C) 2016 Abstract (http://www.abstract.it)
#
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
##############################################################################


from openerp import fields, models, api, _
from openerp.exceptions import Warning as UserError


class DdTCheckMixin(models.AbstractModel):
    _name = "ddt.check.mixin"

    has_ddt_msg = fields.Text(
        default=lambda self: self._get_has_ddt_msg()
    )

    @api.model
    def _get_has_ddt_msg(self):
        if not self.env.context.get('active_ids'):
            return ''
        pickings = self.env['stock.picking'].browse(
            self.env.context.get('active_ids'))
        return self.check(pickings)

    have_ddt_single_err_msg = \
        _("Selected Picking already have a DdT attached.")
    have_ddt_multi_err_msg = \
        _("Selected Pickings `%s` already have a DdT attached.")

    @api.model
    def check(self, pickings, raise_exc=False):
        """Check if given pickings have a DdT.

        Return a msg containing errors
        or if `raise_exc` is passed throws and exception.
        """
        have_ddt = []
        for item in pickings:
            if item.ddt_ids:
                have_ddt.append(item.name)

        msg = ''
        if have_ddt:
            if len(have_ddt) == 1:
                msg = self.have_ddt_single_err_msg
            else:
                msg = self.have_ddt_multi_err_msg % ', '.join(have_ddt)
        if msg:
            if raise_exc:
                raise UserError(msg)
            else:
                msg = self.translate(msg)
        return msg

    @api.model
    def translate(self, term):
        """Load `term` translation."""
        translations = self.env['ir.translation']
        name = ''  # can ben empty since we are passing the source = term
        _type = 'code'
        lang = self.env.context.get('lang')
        return translations._get_source(name, _type, lang, source=term)
