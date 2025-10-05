from odoo import fields, models,api
from datetime import date


class ReturnBook(models.TransientModel):
	"""Defining Book Name."""

	_name = "return.book.wiz"
	_description = "Return Book"

	student_id = fields.Many2one("student.student", string="Student")
	reg_no = fields.Char(related='student_id.reg_no')
	address = fields.Char(related='student_id.street')
	stud_class = fields.Many2one('school.standard', related='student_id.standard_id', sring="Class")
	date = fields.Date("Return Date", default=date.today())
	return_line = fields.One2many('return.book.line', 'return_id')


	@api.model
	def default_get(self, fields_list):
		res = super(ReturnBook, self).default_get(fields_list)
		active_id = self._context.get('active_id')
		if active_id:
			issue = self.env['library.book.issue'].browse(active_id)
			res['student_id'] = issue.student_id.id
			res['return_line'] = [
				(0, 0, {
					'book_id': line.book_id.id,
				}) for line in issue.issue_line if not line.return_date
			]
		return res


	def action_confirm(self):
		active_id = self._context.get('active_id')
		print("Ative id =,", active_id)
		# if not active_id:
		# 	return
		if active_id:
			issue = self.env['library.book.issue'].browse(active_id)
			print("Issue=", issue)
			returned_books = self.return_line.mapped('book_id')
			print("Return book,", returned_books)
			for line in issue.issue_line:
				if line.book_id in returned_books:
					line.return_date = self.date
					line.book_id.issued_qty -= 1

			# if all(line.return_date for line in issue.issue_line):
			# 	issue.is_returned = True

		return {'type': 'ir.actions.act_window_close'}








class BookBookLine(models.TransientModel):
	_name = 'return.book.line'
	_description = "Return Book Line"

	return_id = fields.Many2one('return.book.wiz')
	book_id = fields.Many2one('book.book')
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


# def create_new_books(self):
# 	for rec in self:
# 		rec.create({"name": rec.name.id, "card_id": rec.card_id.id})
