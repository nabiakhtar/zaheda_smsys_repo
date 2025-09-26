# See LICENSE file for full copyright and licensing details.

from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError



#
# class StudentMarks(models.Model):
#     _name = 'student.marks'
#     _description = 'Student Marks'
#
#
#
#     exam_id = fields.Many2one("school.exam", string='Exam')
#     session_id = fields.Many2one('academic.year', 'Academic Year')
#     subject_id = fields.Many2one('subject.subject', string='Subject')
#     marks = fields.Integer('Object Marks')
#     student_id = fields.Many2one('student.student', string='Student')
#
#
#
#
#
# class StudentMarks(models.Model):
#     _name = 'enter.marks'
#     _description = 'Enter Marks'
#
#     exam_id = fields.Many2one("school.exam", string='Exam')
#     session_id = fields.Many2one('academic.year', 'Academic Year')
#     subject_id = fields.Many2one('subject.subject', string='Subject')
#     marks_ids = fields.One2many('student.marks', )



# student_exam/models/student_exam.py

# from odoo import models, fields

class Exam(models.Model):
    _name = 'student.exam'
    _description = 'Student Exam'

    name = fields.Char('Exam Name', required=True)
    year = fields.Char('Year', required=True)
    exam_date = fields.Date('Exam Date')

    subject_ids = fields.One2many('student.exam.subject', 'exam_id', string='Subjects')


class ExamSubject(models.Model):
    _name = 'student.exam.subject'
    _description = 'Subject for an Exam'

    name = fields.Char('Subject Name', required=True)
    exam_id = fields.Many2one('student.exam', string='Exam')
    marks_ids = fields.One2many('student.exam.mark', 'subject_id', string='Marks')


class StudentExamMark(models.Model):
    _name = 'student.exam.mark'
    _description = 'Student Marks for a Subject'

    student_id = fields.Many2one('student.student', string='Student',  required=True)
    subject_id = fields.Many2one('subject.subject', string='Subject')
    marks = fields.Float('Marks', required=True)
    # exam_id = fields.Many2one('student.exam', related='subject_id.exam_id', string='Exam')
    exam_id = fields.Many2one('student.exam',  string='Exam')













