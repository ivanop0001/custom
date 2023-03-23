from odoo import models, api, fields, _

class ProductProduct(models.Model):
    _inherit = 'product.product'

    helpdesk_tag_id = fields.Many2one(
        comodel_name='helpdesk.ticket.tag',
        string='Helpdesk Tag')
    

    