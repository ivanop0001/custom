from odoo.tests import common
from odoo.exceptions import ValidationError



class Test_Helpdesk_Ivan(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.ticket = self.env["helpdesk.ticket"].create({
            'name': 'Test ticket'
        })
        self.user_id = self.ref('base.user_admin')


    def test_01_ticket(self):
        """Test 01:
        Checking ticket name"""
        self.assertEqual(self.ticket.name, "Test ticket")


    def test_02_ticket(self):
        """Test 02:
        Checking ticket user and set it"""
        self.assertEqual(self.ticket.user_id, self.env['res.users'])
        self.ticket.user_id = self.user_id
        self.assertEqual(self.ticket.user_id.id, self.user_id)

    def test_03_ticket(self):
        """Test 03:
        Checking ticket name is not equal"""
        self.assertFalse(self.ticket.name == "asdfas ticketsdf ")

    def test_04_ticket(self):
        """Test 03:
        Checking time exception"""
        self.ticket.time = 4
        self.assertEqual(self.ticket.time, 4)
        self.ticket.time = 12
        self.assertEqual(self.ticket.time, 12)
        self.assertEqual(len(self.ticket.action_ids.ids), 2)

        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.ticket.time = -7
