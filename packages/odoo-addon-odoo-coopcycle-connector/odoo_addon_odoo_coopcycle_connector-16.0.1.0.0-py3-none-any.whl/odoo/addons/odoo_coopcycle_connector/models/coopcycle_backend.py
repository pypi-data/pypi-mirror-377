from odoo import models, fields, api
import hashlib
import requests
import json
import os

IMPORT_DELTA_BUFFER = 30  # seconds

class CoopcycleBackend(models.Model):
    _name = 'coopcycle.backend'
    _inherit = 'connector.backend'
    app_name = fields.Char('Name', required=True)
    url = fields.Char('URL', required=True)
    verbose = fields.Boolean()
    session_token = fields.Char('Session Token')
    language = fields.Char('Language')
    notify_on_save = fields.Boolean('Notify On Save')
    import_partners_from_date = fields.Datetime(
        string='Import partners from date',
    )

    def connect(self):
        username = self.env['ir.config_parameter'].sudo().get_param('odoo-coopcycle-connector.coopcycle_user', 'admin')
        password = self.env['ir.config_parameter'].sudo().get_param('odoo-coopcycle-connector.coopcycle_password', 'admin')
        instance = self.env['ir.config_parameter'].sudo().get_param('odoo-coopcycle-connector.coopcycle_instance')

        params = {
            '_username': username,
            '_password': password,
        }
        result = requests.post(instance+'/login_check', data=params)
        session_token = result.json()['token']
        return session_token

    def get_all_invoice_line_items(self, params=None, token=None):
        params = params or {}
        headers = {"Authorization": f"Bearer {token}"}
        instance = self.env['ir.config_parameter'].sudo().get_param('odoo-coopcycle-connector.coopcycle_instance')

        result = requests.get(instance+'/invoice_line_items/export', params=params, headers=headers)
        return result
    
    def get_invoice_line_items_grouped_by_organization(self, params=None, token=None):
        params = params or {}
        headers = {"Authorization": f"Bearer {token}"}
        instance = self.env['ir.config_parameter'].sudo().get_param('odoo-coopcycle-connector.coopcycle_instance')

        result = requests.get(instance+'/invoice_line_items/grouped_by_organization', params=params, headers=headers)
        return result

    def import_sale_orders(self):
        backend = self

        self.env['res.partner'].import_batch(backend)
        return True

    @api.model
    def cron_import_sale_orders(self):
        instance = self.env['ir.config_parameter'].sudo().get_param('odoo-coopcycle-connector.coopcycle_instance')
        backend = self.create([{
            'app_name': 'ODOO Coopcycle Connector',
            'url': instance
        }])
        backend.with_delay().import_sale_orders()
