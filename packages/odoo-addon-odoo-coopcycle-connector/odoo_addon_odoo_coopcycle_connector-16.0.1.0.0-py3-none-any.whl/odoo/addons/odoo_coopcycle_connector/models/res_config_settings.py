from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    coopcycle_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Default Coopcycle Product',
        config_parameter='odoo-coopcycle-connector.coopcycle_product_id',
        company_dependent=True,
    )

    coopcycle_tax_id = fields.Many2one(
        comodel_name='account.tax',
        string='Default Coopcycle Tax',
        config_parameter='odoo-coopcycle-connector.coopcycle_tax_id',
        company_dependent=True,
    )

    coopcycle_user = fields.Char(
        string='Coopcycle API Username',
        config_parameter='odoo-coopcycle-connector.coopcycle_user',
        company_dependent=True,
    )

    coopcycle_password = fields.Char(
        string='Coopcycle API Password',
        config_parameter='odoo-coopcycle-connector.coopcycle_password',
        company_dependent=True,
        password=True,
    )

    coopcycle_instance = fields.Char(
        string='Coopcycle Instance URL',
        config_parameter='odoo-coopcycle-connector.coopcycle_instance',
        company_dependent=True,
        placeholder='my_company.coopcycle.org',
    )

    coopcycle_sync_max_days = fields.Integer(
        string='Coopcycle Sync Max Days',
        config_parameter='odoo-coopcycle-connector.coopcycle_sync_max_days',
        company_dependent=True,
        help='Maximum number of past days to sync Coopcycle orders.',
    )