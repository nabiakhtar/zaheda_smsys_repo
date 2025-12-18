# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BuildResult(models.TransientModel):
	_name = 'build.result.wiz'
	_description = 'Mark Slip'

	exam_id = fields.Many2one("exam.exam", "Exam", help="exam")
	school_ids = fields.Many2many(
		'school.school',
		string="Schools"
	)

	class_ids = fields.Many2many(
		'school.standard',
		string="Classes",
		domain="[('school_id', 'in', school_ids)]"
	)

	def cal_all_result(self):
		domain = [
			('exam_id', '=', self.exam_id.id),
			('class_id', 'in', self.class_ids.ids),
		]
		print("Domain=", domain)
		results = self.env['exam.result'].search(domain)
		for result in results:
			if not result.is_cald:
				total = 0
				for rec in result.student_marks_ids:
					passing_marks = 34
					grace_max_marks = 20
					remain_grace_mark = grace_max_marks
					sorted_records = sorted(rec, key=lambda record: record.mo1 + record.mo2, reverse=True)
					print("Sored ", sorted_records)
					total_grace_added = 0
					total_marks_obtained = 0
					rec.grace_mark = 0

					for rec in sorted_records:
						mark = rec.mo1 + rec.mo2
						if mark < passing_marks:
							required_grace = passing_marks - mark
							grace_for_subject = min(required_grace, grace_max_marks)
							remaining_grace = grace_max_marks - total_grace_added
							grace_for_subject = min(grace_for_subject, remaining_grace)
							rec.grace_mark = grace_for_subject
							total_grace_added += grace_for_subject
						else:
							rec.grace_mark = 0

						rec.total_mark = mark + rec.grace_mark
						total += rec.total_mark

				result.total = total
				total_mark = int(len(result.student_marks_ids))
				percentage = round(total / total_mark, 2)
				result.percentage = percentage
				result.is_cald = True
				result.state = 'confirm'


	def print_all_result(self):
		"""Print all selected class results in one PDF"""
		if not self.class_ids:
			raise UserError("Please select at least one class.")

		# Pass exam + classes to report
		data = {
			"exam_id": self.exam_id.id,
			"class_ids": self.class_ids.ids,
		}

		return self.env.ref("up_exam.report_exam_result").report_action(self, data=data)



	@api.model
	def _get_report_values(self, docids, data=None):
		classes = self.env['school.standard'].browse(data['class_ids'])
		exam = self.env['exam.exam'].browse(data['exam_id'])

		result_data = []

		for cls in classes:
			students = self.env['student.student'].search([('standard_id', '=', cls.id),('state', '=', 'done')])
			subjects = cls.subject_ids

			result_data.append({
				'class': cls,
				'students': students,
				'subjects': subjects,
				'exam': exam,
			})

		return {
			'doc_ids': data['class_ids'],
			'doc_model': 'school.standard',
			'data': result_data,
		}

# def action_create_mark_slip(self):
#     ExamResult = self.env['exam.result']
#     Student_marks = self.env['student.marks']
#
#     for wizard in self:
#         classes = wizard.class_ids
#         print("Classes=", classes)
#
#         for std_class in classes:
#
#             # Get students of class
#             students = self.env['student.student'].search([
#                 ('standard_id', '=', std_class.id)
#             ])
#             print("Student==", students, )
#
#             # Get subjects of class
#             subjects = std_class.subject_ids
#             print("sub-", subjects)
#
#             for student in students:
#                 for subject in subjects:
#                     # Check if record already exists (avoid duplicates)
#                     result_id = ExamResult.search([
#                         ('exam_id', '=', wizard.exam_id.id),
#                         ('class_id', '=', std_class.id),
#                         ('student_id', '=', student.id),
#                     ], limit=1)
#                     if not result_id:
#                         result_id = ExamResult.create(
#                             {
#                                 'exam_id': wizard.exam_id.id,
#                                 'school_id': std_class.school_id.id,
#                                 'class_id': std_class.id,
#                                 'student_id': student.id,
#                             }
#                         )
#
#                     student_marks = Student_marks.search([
#                         ("exam_result_id", '=', result_id.id),
#                         ("subject_id", '=', subject.id),
#                     ])
#                     if not student_marks:
#                         student_marks = Student_marks.create({
#                             "exam_result_id": result_id.id,
#                             "subject_id": subject.id,
#                             "mo1": 0,
#                             "mo2": 0,
#                             "grace_mark": 0,
#                             "total_mark": 0,
#                         })
#
#
#                     # ===================================
#
#     return {
#         'type': 'ir.actions.client',
#         'tag': 'display_notification',
#         'params': {
#             'title': _("Success"),
#             'message': _("Mark slip created successfully."),
#             'type': 'success',
#             'sticky': False,
#         }
#     }
