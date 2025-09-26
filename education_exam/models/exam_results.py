# -*- coding: utf-8 -*-
from docutils.parsers.rst.directives import percentage

from odoo import models, fields, api
from odoo.tools.populate import compute


class EducationExamResults(models.Model):
    _name = 'education.exam.results'
    _description = 'Exam Results'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name')
    exam_id = fields.Many2one('education.exam', string='Exam')
    class_id = fields.Many2one('school.standard', string='Class')
    division_id = fields.Many2one('standard.division', string='Division')
    student_id = fields.Many2one('student.student', string='Student')
    student_name = fields.Char(string='Student')
    subject_line = fields.One2many('results.subject.line', 'result_id',string='Subjects')

    academic_year = fields.Many2one('academic.year',
                                    string='Academic Year',
                                    # related='division_id.academic_year_id',
                                    store=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    total_pass_mark = fields.Integer(string='Total Pass Mark', store=True,
                                   readonly=True)
    total_max_mark = fields.Integer(string='Total Max Mark',
                                  readonly=True,  store=True)
    total_mark_scored = fields.Integer(string='Total Marks Scored',
                                     readonly=True ,store=True)

    total_grace_mark = fields.Integer(string='Total Grace Mark',
                                       readonly=True, store=True)
    percentage = fields.Float("Percentage",)
    division = fields.Char(string="Division", store=True)


    result_status = fields.Char(string="Result")
    stud_position = fields.Integer(string="Position")



    def cal_division(self, percentage):
        if percentage:
            if percentage > 59:
                return "I"
            if percentage > 49:
                return "II"
            return "III"
        return ''



    #
    # def calculate_position(self, student_score, all_scores):
    #     # Sort the scores in descending order to rank the students
    #     sorted_scores = sorted(all_scores, reverse=True)
    #     # Find the position of the student's score in the sorted list
    #     position = sorted_scores.index(student_score) + 1
    #     return position
        # for results in self.search([('exam_id', '=', self.exam_id.id),('class_id', '=', self.class_id.id)]):
        for results in self:
            total_pass_mark = 0
            total_max_mark = 0
            total_mark_scored = 0
            total_grace_mark = 0
            for subjects in results.subject_line:
                subjects.mark_scored_et = subjects.mark_scored_e1 + subjects.mark_scored_e2 + subjects.grace_mark
                subjects.max_mark_et = subjects.max_mark_e1 + subjects.max_mark_e2

                total_max_mark += subjects.max_mark_et
                total_mark_scored += subjects.mark_scored_et
                total_grace_mark += subjects.grace_mark
            results.total_pass_mark = total_pass_mark
            results.total_max_mark = total_max_mark
            results.total_mark_scored = total_mark_scored
            results.total_grace_mark = total_grace_mark

            percentage = (results.total_mark_scored / total_max_mark if total_max_mark else 1) * 100
            results.percentage = round(percentage, 2)
            results.division = self.cal_division(results.percentage)

            count_below_34 = len(list(filter(lambda mark: mark < 34, results.subject_line.mapped('mark_scored_et'))))
            result = 'کامیاب'
            if count_below_34 == 1:
                result = 'ترقی'

            if count_below_34 > 1:
                result = 'نا کام'
            results.result_status = result

            position = results.search([('exam_id', '=', results.exam_id.id),])
            print("Posion===",position )


    # @api.depends('total_grace_mark', 'total_max_mark', 'total_mark_scored')
    def cal_student_position(self):
        all_scores = self.search([
            ('exam_id', '=', self.exam_id.id),
            ('class_id', '=', self.class_id.id)
        ], order='total_mark_scored desc')
        position = 1
        for rec in all_scores:
            print("rec=",rec.total_mark_scored)
            if rec.total_grace_mark > 0:
                rec.stud_position = 0
            else:
                rec.stud_position = position
                position += 1



class ResultsSubjectLine(models.Model):
    _name = 'results.subject.line'
    _description = 'Results Subject Line'

    name = fields.Char(string='Name')
    subject_id = fields.Many2one('subject.subject', string='Subject')
    max_mark = fields.Integer(string='Max Mark Exam')
    max_mark_e1 = fields.Integer(string='Max Mark Exam-1')
    max_mark_e2 = fields.Integer(string='Max Mark Exam-2')
    max_mark_et = fields.Integer(string='Max Mark Total',)
    pass_mark = fields.Integer(string='Pass Mark')
    mark_scored = fields.Integer(string='Mark Scored Exam')
    mark_scored_e1 = fields.Integer(string='Mark Scored Exam-1')
    mark_scored_e2 = fields.Integer(string='Mark Scored Exa-2',)
    grace_mark = fields.Integer(string='Grace Mark',compute='_cal_grace_mark')
    mark_scored_et = fields.Integer(string='Mark Scored Total')
    pass_or_fail = fields.Boolean(string='Pass/Fail')
    result_id = fields.Many2one('education.exam.results', string='Result Id')
    exam_id = fields.Many2one('education.exam', string='Exam')
    class_id = fields.Many2one('school.standard', string='Class')
    division_id = fields.Many2one('standard.division', string='Division')
    student_id = fields.Many2one('student.student', string='Student')
    student_name = fields.Char(string='Student')
    academic_year = fields.Many2one('academic.year',string='Academic Year',
                                    # related='division_id.academic_year_id',
                                    store=True)


    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get())


    # def cal_f(self):
    @api.depends('mark_scored_e1', 'mark_scored_e2')
    def _cal_grace_mark(self):
        passing_marks = 34
        grace_max_marks  = 20
        remain_grace_mark = grace_max_marks
        sorted_records = sorted(self, key=lambda record: record.mark_scored_e1 + record.mark_scored_e2, reverse=True)
        total_grace_added = 0
        total_marks_obtained = 0
        self.grace_mark = 0

        for rec in sorted_records:
            mark = rec.mark_scored_e1 + rec.mark_scored_e2
            if mark < passing_marks:
                required_grace = passing_marks - mark
                grace_for_subject = min(required_grace, grace_max_marks)
                remaining_grace = grace_max_marks - total_grace_added
                grace_for_subject = min(grace_for_subject, remaining_grace)
                rec.grace_mark = grace_for_subject
                total_grace_added += grace_for_subject
            else:
                rec.grace_mark = 0
