# Copyright <2021> AEODOO>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Helpdesk Angel Moya",
    "version": "14.0.1.0.0",
    "author": "AEODOO, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "base",
    ],
    "data": [
        "data/delete_tag_cron.xml",
        "security/helpdesk_security.xml",
        "security/ir.model.access.csv",
        "views/helpdesk_menu.xml",
        "wizards/create_ticket_view.xml",
        "views/helpdesk_tag_view.xml",
        "views/helpdesk_view.xml",
    ],
}