from pkg_resources import require

from odoo import _, api, fields, models
from odoo.addons.test_impex.models import field
from datetime import date, timedelta
from odoo.exceptions import ValidationError

from odoo.tools.populate import compute


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
	book_code_line = fields.One2many('book.code.line', 'book_id')


	def _cal_available_qty(self):
		for rec in self:
			rec.available_qty = rec.qty - rec.issued_qty

	def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
		args = args or []
		domain = []
		if name:
			# Search by reg_no OR by name
			domain = ['|', ('code', operator, name), ('name', operator, name)]
		return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)

class BookCodeLine(models.Model):
	_name = 'book.code.line'
	_description = 'Book Code Line'


	name = fields.Char(string='Book Unique Code')
	srno = fields.Integer(string="SR-NO", compute='_compute_sr_no')
	note = fields.Char(string="Note")
	book_id = fields.Many2one('book.book')


	@api.depends('book_id.book_code_line')
	def _compute_sr_no(self):
		"""Auto-generate Sr. No. based on position in one2many list."""
		for rec in self:
			if rec.book_id:
				# Sort by list order
				lines = rec.book_id.book_code_line
				for idx, line in enumerate(lines, start=1):
					line.srno = idx




class BookIssue(models.Model):
	_name = 'library.book.issue'
	_description = 'Library Book Issue'

	name = fields.Char(
		string="Book Issue ",
		required=True, copy=False, readonly=True,
		index='trigram',
		states={'draft': [('readonly', False)]},
		default=lambda self: 'New')


	student_id = fields.Many2one("student.student", string="Student")
	reg_no = fields.Char(related='student_id.reg_no')
	address = fields.Char(related='student_id.street')
	stud_class = fields.Many2one('school.standard',related='student_id.standard_id', sring="Class")
	date = fields.Date("Date Issue", default=date.today())
	issue_line = fields.One2many('book.book.line', 'issuse_id')
	state = fields.Selection(
		[
			("draft", "Draft"),
			("issue", "Issued"),
			("cancel", "Cancel"),
			("return", "Returned"),
		],
		default="draft",
		help="State of the library book",
	)

	is_returned = fields.Boolean("All Books Returned",compute='_cal_all_returned',store=False, default=False)


	def confirm_issue(self):
		self.state = 'issue'

		for rec in self.issue_line:
			rec.book_id.issued_qty += 1

	@api.depends('state','is_returned')
	def _cal_all_returned(self):
		for rec in self:
			rec.is_returned = False
			if all(line.return_date for line in rec.issue_line):
				rec.is_returned = True
			if rec.is_returned:
				rec.state = 'return'


	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			vals['name'] = self.env['ir.sequence'].next_by_code('book.issue.seq') or 'New'
		return super(BookIssue, self).create(vals)


	def return_book(self):
		if self.is_returned:
			return None
		return {
			'name': 'Return Book',
			'type': 'ir.actions.act_window',
			'res_model': 'return.book.wiz',
			'view_mode': 'form',
			'target': 'new',  # opens as popup
			'context': {
				# 'default_student_id': self.student_id.id,
				'default_date': fields.Date.context_today(self),
			}
		}





class BookBookLine(models.Model):
	_name = 'book.book.line'
	_description = "Book Book Line"
	_rec_name = 'book_id'

	issuse_id = fields.Many2one('library.book.issue')
	book_id = fields.Many2one('book.book')
	book_unique_code = fields.Char("Book Unique Code")
	issue_date = fields.Date(string="Issue Date", related="issuse_id.date", store=True, readonly=False)
	return_date = fields.Date(string="Return Date", readonly=True) #make readonly true

	return_days = fields.Integer(string="Return days", related='book_id.issue_duration')
	Remark = fields.Char(string="Remark")
	state = fields.Selection(
		[
			("draft", "Draft"),
			("issue", "Issued"),
			("cancel", "Cancelled"),
			("return", "Returned"),
			("lost", "Lost"),
		],
		default="draft",
		help="State of the library book",
	)
	is_due = fields.Boolean(string="Is Due", compute='_compute_is_due', store=True)

	@api.depends('issue_date', 'book_id.issue_duration', 'state', 'return_date')
	def _compute_is_due(self):
		for rec in self:
			# if rec.state == 'issue' and rec.issue_date:
			if rec.issue_date:
				due_date = rec.issue_date + timedelta(days=rec.book_id.issue_duration)
				rec.is_due = (date.today() > due_date and not rec.return_date)
			else:
				rec.is_due = False

	@api.onchange('book_unique_code')
	def search_book(self):
		if self.book_unique_code:
			uniq_id = self.env['book.code.line'].search([('name', '=', self.book_unique_code)], limit=1)
			if not uniq_id:
				raise ValidationError(_('No Book found for this Unique Code'))
			print("uniq_id=========",uniq_id)
			book_id = self.env['book.book'].search([('id', '=', uniq_id.book_id.id)], limit=1)
			if book_id:
				self.book_id = book_id.id
			print("book=======", book_id)









