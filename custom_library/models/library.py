from pkg_resources import require

from odoo import _, api, fields, models
from odoo.addons.test_impex.models import field


class Book(models.Model):
	_name = 'book.book'
	_description = 'Book'

	name = fields.Char(string='Book Name', require=True)
	code = fields.Char(string="Book Code")
	book_author = fields.Char("Author")
	qty = fields.Integer(string="Qty")
	issued_qty = fields.Integer(string="Issued Qty")
	available_qty = fields.Integer(string="Available Qty", compute='_cal_available_qty')
	price = fields.Float(string="Price")
	location = fields.Char("Location")
	sub_location = fields.Char("Sub Location")
	issue_duration = fields.Integer(string='Issue Duration')

	def _cal_available_qty(self):
		for rec in self:
			rec.available_qty = rec.qty - rec.issued_qty


class BookIssue(models.Model):
	_name = 'library.book.issue'
	_description = 'Library Book Issue'

	student_id = fields.Many2one("student.student", string="Student")
	reg_no = fields.Char(related='student_id.reg_no')
	address = fields.Char(related='student_id.street')
	stud_class = fields.Many2one('school.standard', sring="Class")
	date = fields.Date("Date Issue")
	issue_line = fields.One2many('book.book.line', 'issuse_id')


class BookBookLine(models.Model):
	_name = 'book.book.line'
	_description = "Book Book Line"

	issuse_id = fields.Many2one('library.book.issue')
	book_id = fields.Many2one('book.book')
	issue_date = fields.Date(string="Issue Date")
	return_days = fields.Integer(string="Return days", related='book_id.issue_duration')
	# to_be_return_on_date = fields.Date(string="To be Return", related='book_id.issue_duration')
	Remark = fields.Char(string="Remark")


