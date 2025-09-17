# Copyright 2013-2019 Camptocamp SA
# © 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import models, fields, api
from odoo.addons.component.core import Component
from math import ceil
from datetime import datetime, timedelta
from stdnum.eu import vat
import html

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    coopcycle_bind_id = fields.Integer(
        string="Coopcycle Partner ID",
        company_dependent=True,
        tracking=True
    )

    @api.model
    def import_batch(self, backend):
        token = backend.connect()
        tomorrow = datetime.today() + datetime.timedelta(days=1)
        tomorrow.strftime('%Y-%m-%d')
        maxSyncDays = self.env['ir.config_parameter'].sudo().get_param('odoo-coopcycle-connector.coopcycle_sync_max_days', 7)
        dateAfter = datetime.today()- timedelta(days=int(maxSyncDays))
        dateAfter.strftime('%Y-%m-%d')
        params = {
            'state[]': ['new', 'accepted', 'fullfilled'],
            'date[after]': dateAfter,
            'date[before]': tomorrow,
            'page': 1,
            'itemsPerPage': 10,
        }

        self.update_partners_list(backend, params, token)
        rsps = self.env['res.partner'].search([('coopcycle_bind_id', '!=', False)])
        for partner in rsps:
            partner.get_unprocessed_order_lines(params, backend, token)

    @api.model
    def update_partners_list(self, backend, params, token):
        result2 = backend.get_invoice_line_items_grouped_by_organization(params, token)
        for organization in result2.json()['hydra:member']:
            sID = organization['storeId']
            rsp = self.env['res.partner'].search([('coopcycle_bind_id', '=', sID)])
            if not rsp:
                name = organization['organizationLegalName']
                rsp = self.env['res.partner'].search([('name', '=', name)])
                if rsp:
                    self.env['res.partner'].edit([{
                        'coopcycle_bind_id': organization['storeId']
                    }])
            if not rsp:
                self.env['res.partner'].create([{
                    'coopcycle_bind_id': organization['storeId'],
                    'name': organization['organizationLegalName']
                }])

    def get_unprocessed_order_lines(self,params, backend, token):
        params['store'] = self.coopcycle_bind_id
        result = backend.get_all_invoice_line_items(params, token)
        uom = self.env.ref('uom.product_uom_unit')
        productID = self.env['ir.config_parameter'].sudo().get_param('odoo-coopcycle-connector.coopcycle_product_id')
        coopcycle_tax_id = self.env['ir.config_parameter'].sudo().get_param('odoo-coopcycle-connector.coopcycle_tax_id')
        tax = self.env['account.tax'].search([('id', '=', coopcycle_tax_id)])

        lis = []
        for lineitem in result.json()['hydra:member']:
            iD = lineitem['@id'].split('/')[-1]
            sol = self.env['sale.order.line'].search([('coopcycle_id', '=', iD)])
            price = lineitem['Total products (excl. VAT)']

            if not sol:
                lis.append((0, 0, {'name': lineitem['Description'], 
                                   'product_id': productID,
                                   'tax_id': [(4,tax[0].id)],
                                   'price_unit': price,
                                   'coopcycle_id': iD,
                                   'product_uom': uom.id, 
                                   'product_uom_qty': 1,}))
                
        if lis:        
            self.env['sale.order'].create({
                'name': 'Sale order',
                'partner_id': self.id,
                'is_coopcycle_import': True,
                'order_line': lis
            })