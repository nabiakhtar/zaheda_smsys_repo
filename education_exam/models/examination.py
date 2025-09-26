# -*- coding: utf-8 -*-
###############################################################################
#    A part of Educational ERP Project <https://www.educationalerp.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2020-TODAY Cybrosys Technologies (<https://www.cybrosys.com>)
#    Author: Hajaj Roshan (hajaj@cybrosys.in)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
################################################################################
from email.policy import default

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EducationExam(models.Model):
    _name = 'education.exam'
    _description = 'Education Exam'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', default='New')
    class_id = fields.Many2one('school.standard', string='Class')
    division_id = fields.Many2one('standard.division', string='Division')
    exam_type = fields.Many2one('education.exam.type', string='Type',
                                required=True)
    school_class_division_wise = fields.Selection(
        [('school', 'School'), ('class', 'Class'), ('division', 'Division')],
        related='exam_type.school_class_division_wise',
        string='School/Class/Division Wise')
    class_division_hider = fields.Char(string='Class Division Hider')
    start_date = fields.Date(string='Start Date', required=False)
    end_date = fields.Date(string='End Date', required=False)
    subject_line = fields.One2many('education.subject.line', 'exam_id',
                                   string='Subjects')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('ongoing', 'On Going'),
         ('close', 'Closed'),
         ('cancel', 'Canceled')],
        default='draft')
    academic_year = fields.Many2one('academic.year',
                                    string='Academic Year',
                                    default=lambda self: self.env['academic.year'].search([('current', '=', True)], limit=1),
                                    store=True)
    # related='division_id.academic_year_id',

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())

    # @api.model
    # def create(self, vals):
        # res = super(EducationExam, self).create(vals)
        # if res.division_id:
        #     res.class_id = res.division_id.class_id.id
        # return res

    def build_students_marks000000000000000000000(self):
        exam_id = self
        domain = [
            ('exam_id', '=', exam_id.id),
        ]
        marks = self.env['results.subject.line'].search(domain)
        # Iterate over the marks and populate the dictionary
        for mark in marks:
            student_name = mark.student_id.name
            subject_name = mark.subject_id.name
            scored_marks = mark.mark_scored
            max_marks = mark.max_mark
            exam_name = mark.exam_id

            print("student_name=", student_name)
            print("subject_name=", subject_name)
            print("scored_marks=", scored_marks)
            print("max_marks=", max_marks)
            print("exam_name=", exam_name.name)
            print("================================")

    @api.onchange('class_division_hider')
    def onchange_class_division_hider(self):
        self.school_class_division_wise = 'school'

    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        for rec in self:
            if rec.start_date > rec.end_date:
                raise ValidationError(
                    _("Start date must be Anterior to end date"))

    def close_exam(self):
        self.state = 'close'

    def cancel_exam(self):
        self.state = 'cancel'

    def confirm_exam(self):
        if len(self.subject_line) < 1:
            raise UserError(_('Please Add Subjects'))
        name = str(self.exam_type.name) + '-' + str(self.start_date)[0:10]
        if self.division_id:
            name = name + ' (' + str(self.division_id.name) + ')'
        elif self.class_id:
            name = name + ' (' + str(self.class_id.name) + ')'
        self.name = name
        self.state = 'ongoing'


    # @api.onchange('class_id')
    def set_subjects(self):
        print("Classs......")
        subject_obj = self.env['education.subject.line']
        for rec in self:
            rec.subject_line = False
            if rec.class_id:
                subjects = self.class_id.subject_ids
                if len(subjects) < 1:
                    raise UserError(_('There is no subject define in this class'))
                subject_lines = []
                for subject in subjects:
                    data = {
                        'subject_id': subject.id,
                        'time_from': 0.0,
                        'time_to': 0.0,
                        'mark': 0,
                        'exam_id': rec.id
                    }
                    subject_lines.append((0, 0, data))
                rec.write({
                    'subject_line': subject_lines,
                })
                # subject_obj.create(data)
                # self.mark_sheet_created = True


class SubjectLine(models.Model):
    _name = 'education.subject.line'
    _description = 'Subject Line'

    subject_id = fields.Many2one('subject.subject', string='Subject',
                                 required=True)
    date = fields.Date(string='Date', required=False)
    time_from = fields.Float(string='Time From', required=True)
    time_to = fields.Float(string='Time To', required=True)
    mark = fields.Integer(string='Mark')
    exam_id = fields.Many2one('education.exam', string='Exam')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())


class EducationExamType(models.Model):
    _name = 'education.exam.type'
    _description = 'Education Exam Type'

    name = fields.Char(string='Name', required=True)
    school_class_division_wise = fields.Selection(
        [('school', 'School'), ('class', 'Class'), ('division', 'Division'),
         ('final', 'Final Exam (Exam that promotes students to the next class)')
         ],
        string='Exam Type', default='class')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())


class MarkSheetCongiguration(models.Model):
    _name = 'education.marksheet.config'
    _description = 'Education Mark Sheet Config'


    name = fields.Char("Name")
    marksheet_report_config_ids = fields.Many2many("education.exam.type",'rel_education_type_marksheet_config', 'edu_marksheet_id', 'exam_type_id')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    academic_year = fields.Many2one('academic.year',
                                    string='Academic Year',
                                    default=lambda self: self.env['academic.year'].search([('current', '=', True)],
                                                                                          limit=1),
                                    store=True)

