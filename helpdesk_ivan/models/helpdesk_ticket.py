from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class HelpdeskTicketAction(models.Model):
    _name = 'helpdesk.ticket.action'
    _description = 'Action'

    name = fields.Char()
    date = fields.Date()
    time = fields.Float(
        string='Time')
    ticket_id = fields.Many2one(
        comodel_name='helpdesk.ticket',
        string='Ticket')


class HelpdeskTicketTag(models.Model):
    _name = 'helpdesk.ticket.tag'
    _description = 'Tag'

    name = fields.Char()
    public = fields.Boolean()
    ticket_ids = fields.Many2many(
        comodel_name='helpdesk.ticket',
        relation='helpdesl_ticket_tag_rel',
        column1='tag_id',
        column2='ticket_id',
        string='Tickets')

    @api.model
    def cron_delete_tag(self):
        tickets = self.search([('ticket_ids', '=', False)])
        tickets.unlink()


class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _description = 'Ticket'

    _inherit = ['mail.activity.mixin',
                'mail.thread.cc',
                'mail.thread.blacklist']

    _primary_email = 'email_from'
    def _date_default_today(self):
        return fields.Date.today()

    @api.model
    def default_get(self, dafault_fields):
        vals = super(HelpdeskTicket, self).default_get(dafault_fields)
        vals.update({'date': fields.Date.today() + timedelta(days=1)})
        return vals

    name = fields.Char(
        string='Name',
        required=True)
    description = fields.Text(
        string='Description',
        translate=True)
    date = fields.Date(
        string='Date')
    email_from = fields.Char(string='Email from')
    state = fields.Selection(
        [('nuevo', 'Nuevo'),
         ('asignado', 'Asignado'),
         ('proceso', 'En proceso'),
         ('pendiente', 'Pendiente'),
         ('resuelto', 'Resuelto'),
         ('cancelado', 'Cancelado')],
        string='State',
        default='nuevo')
    time = fields.Float(
        string='Time',
        compute='_get_time',
        inverse='_set_time',
        search='_search_time')
    assigned = fields.Boolean(
        string='Assigned',
        compute='_compute_assigned')
    date_limit = fields.Date(
        string='Date Limit')
    action_corrective = fields.Html(
        string='Corrective Action',
        help='Descrive corrective actions to do')
    action_preventive = fields.Html(
        string='Preventive Action',
        help='Descrive preventive actions to do')
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Assigned to')
    tag_ids = fields.Many2many(
        comodel_name='helpdesk.ticket.tag',
        relation='helpdesl_ticket_tag_rel',
        column1='ticket_id',
        column2='tag_id',
        string='Tags')
    action_ids = fields.One2many(
        comodel_name='helpdesk.ticket.action',
        inverse_name='ticket_id',
        string='Ations')
    partner_id = fields.Many2one('res.partner', string='Partner')

    @api.depends('action_ids.time')
    def _get_time(self):
        for record in self:
            record.time = sum(record.action_ids.mapped('time'))

    def _set_time(self):
        for record in self:
            if record.time:
                time_now = sum(record.action_ids.mapped('time'))
                next_time = record.time - time_now
                if next_time:
                    data = {'name': '/', 'time': next_time,
                            'date': fields.Date.today(), 'ticket_id': record.id}
                    self.env['helpdesk.ticket.action'].create(data)

    def _search_time(self, operator, value):
        actions = self.env['helpdesk.ticket.action'].search(
            [('time', operator, value)])
        return [('id', 'in', actions.mapped('ticket_id').ids)]

    def asignar(self):
        self.ensure_one()
        self.write({
            'state': 'asignado',
            'assigned': True})

    def proceso(self):
        self.ensure_one()
        self.state = 'proceso'

    def pendiente(self):
        self.ensure_one()
        self.state = 'pendiente'

    def finalizar(self):
        self.ensure_one()
        self.state = 'resuelto'

    def cancelar(self):
        self.ensure_one()
        self.state = 'cancelado'

    def cancelar_multi(self):
        for record in self:
            record.cancelar()

    @api.depends('user_id')
    def _compute_assigned(self):
        for record in self:
            record.assigned = self.user_id and True or False

    # hacer un campo calculado que indique, dentro de un ticket,
    # la cantidad de tiquets asociados al mismo ususario.
    ticket_qty = fields.Integer(
        string='Ticket Qty',
        compute='_compute_ticket_qty')

    @api.depends('user_id')
    def _compute_ticket_qty(self):
        for record in self:
            other_tickets = self.env['helpdesk.ticket'].search(
                [('user_id', '=', record.user_id.id)])
            record.ticket_qty = len(other_tickets)

    # crear un campo nombre de etiqueta, y hacer un botón que cree la nueva etiqueta con ese nombre y lo asocie al ticket.
    tag_name = fields.Char(
        string='Tag Name')

    def create_tag(self):
        self.ensure_one()
        # opción 1
        # self.write({
        #     'tag_ids': [(0,0, {'name': self.tag_name})]
        # })
        # # opción 2
        # tag = self.env['helpdesk.ticket.tag'].create({
        #     'name': self.tag_name
        # })
        # self.write({
        #     'tag_ids': [(4,tag.id, 0)]
        # })
        # # opción 3
        # tag = self.env['helpdesk.ticket.tag'].create({
        #     'name': self.tag_name
        # })
        # self.write({
        #     'tag_ids': [(6, 0, tag.ids)]
        # })
        # # opción 4
        # tag = self.env['helpdesk.ticket.tag'].create({
        #     'name': self.tag_name,
        #     'ticket_ids': [(6, 0, self.ids)]
        # })
        # self.tag_name = False

        # pasa por contexto el valor del nombre y la relación con el ticket.
        action = self.env.ref('helpdesk_ivan.action_new_tag').read()[0]
        action['context'] = {
            'default_name': self.tag_name,
            'default_ticket_ids': [(6, 0, self.ids)]
        }
        # action['res_id'] = tag.id
        self.tag_name = False
        return action

    @api.constrains('time')
    def _time_positive(self):
        for ticket in self:
            if ticket.time and ticket.time < 0:
                raise ValidationError(_("The time can not be negative."))

    @api.onchange('date', 'time')
    def _onchange_date(self):
        self.date_limit = self.date and self.date + timedelta(hours=self.time)
