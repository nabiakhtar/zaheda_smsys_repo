# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_


class SubjectResultWiz(models.TransientModel):
    _name = "subject.marks.wiz"
    _description = "Subject Wise Result"

    exam_id = fields.Many2one("exam.exam", "Exam", help="exam")
    school_id = fields.Many2one("school.school","School",required=True, help="School of the following standard")
    class_id = fields.Many2one("school.standard")
    section_id = fields.Many2one("standard.division")
    # academic_year_id = fields.Many2one("academic.year", "Academic Year",default=lambda self: self.env['academic.year'].search([('current', '=', True)], limit=1), help="Academic Year")
    # exam_term = fields.Selection([('e1', 'Test 1'), ('e2', 'Test 2'),('e3', 'Test 3'), ('e4', 'Test 4')])
    exam_term = fields.Selection([('e1', 'Half Yearly Exam'), ('e2', 'Final Exam')])
    subject_id = fields.Many2one('subject.subject')
    student_marks_ids = fields.One2many('student.marks.line', 'wizard_id', string='Student Marks')

    @api.onchange('class_id')
    def _onchange_class_ids(self):
        all_subjects = self.class_id.mapped('subject_ids')
        print("All subjects =", all_subjects)
        return {'domain': {'subject_id': [('id', 'in', all_subjects.ids)]}}

    @api.onchange('school_id')
    def _onchange_school_id(self):
        self.student_marks_ids = [(5, 0, 0)]

    @api.onchange('class_id')
    def _onchange_class_id(self):
        if self.class_id:
            self.student_marks_ids = [(5, 0, 0)]
            students = self.env['student.student'].search([
                ('standard_id', '=', self.class_id.id),
                ('state', '=', 'done')
            ])
            lines = []
            for student in students:
                lines.append((0, 0, {
                    'student_id': student.id,
                    'marks': 0.0,  # default marks
                }))
            self.student_marks_ids = lines
        else:
            self.student_marks_ids = [(5, 0, 0)]  #


    # @api.onchange('subject_id')
    # def _onchange_subject(self):
    #     if self.exam_id and self.school_id and self.exam_term and self.class_id:
    #         self.student_marks_ids = False
    #         marks = self.env['student.marks'].search([
    #             ('academic_year_id', '=', self.exam_id.academic_year.id),
    #             ('subject_id', '=', self.subject_id.id),
    #             ('standard_id', '=', self.class_id.id),
    #         ])
    #         # marline = self.env['student.marks.line'].search([('wizard_id', '=', self.id)])
    #         print("m=", marks)
    #         # print("marline=", marline)
    #         lines = []
    #         for m in marks:
    #             lines.append((0, 0, {
    #                 'student_id': m.student_id.id,
    #                 'marks':  m.mo1 if self.exam_term == 'e1' else m.mo2
    #             }))
    #         self.student_marks_ids = lines




    def add_marks(self):
        print("Add marks.........")
        exam_result_obj = self.env['exam.result']
        student_mark_obj = self.env['student.marks']
        print("ccc", self.student_marks_ids)
        for rec in self.student_marks_ids:
            print("Add Marks.............", rec)
            student_id = rec.student_id
            print("Student=", rec.student_id, rec.roll_no, rec.reg_no)
            exam_result = exam_result_obj.search([
                ('exam_id', '=', self.exam_id.id),
                ('student_id', '=', student_id.id),
                ('class_id', '=', self.class_id.id),
            ])
            if not exam_result:
                exam_result = exam_result_obj.create(
                    {
                        'exam_id': self.exam_id.id,
                        'student_id':  student_id.id,
                        'class_id':  self.class_id.id,
                        'reg_no': rec.reg_no,
                        'roll_no': rec.roll_no,
                    })
            student_marks = student_mark_obj.search([
                ("exam_result_id", '=', exam_result.id),
                ("subject_id", '=', self.subject_id.id),
            ])
            if not student_marks:
                student_marks = student_mark_obj.create({
                    "exam_result_id": exam_result.id,
                    "subject_id": self.subject_id.id,
                    "student_id" : student_id.id,
                    "reg_no" : student_id.reg_no,
                    "roll_no" : student_id.roll_no,
                    "standard_id": self.class_id.id,
                    "academic_year_id": self.exam_id.academic_year.id
                })
            if self.exam_term == 'e1':
                student_marks.mo1 = rec.marks
            if self.exam_term == 'e2':
                student_marks.mo2 = rec.marks
            # if self.exam_term == 'e3':
            #     student_marks.mo3 = rec.marks
            # if self.exam_term == 'e4':
            #     student_marks.mo4 = rec.marks

    def result_report(self):
        """Method to get the result report"""
        data = self.read()[0]
        return self.env.ref("exam.add_exam_result_id_qweb").report_action([], data=data)

    # def action_print_markslip(self):
    #     classes = self.class_ids.ids
    #     data = {
    #         'classes': classes,
    #         'academic_year': self.exam_id.academic_year.name or ''
    #     }
    #     return self.env.ref('up_exam.mark_slip_report_action').report_action(self, data=data)

    # def action_print_markssummary(self):
    #     example_id = self.exam_id
    #     classes = self.class_ids.ids
    #     data = {
    #         # 'print_separate': self.print_separate,
    #         'classes': classes,
    #         'exam': example_id.id
    #     }
    #     return self.env.ref('up_exam.mark_summary_report_action').report_action(self, data=data)

class SubjectResultLine(models.TransientModel):
    _name = 'student.marks.line'
    _description = 'Subject Result Line'
    _order = 'roll_no asc'

    wizard_id = fields.Many2one('subject.marks.wiz', string='Wizard')
    student_id = fields.Many2one('student.student', string='Student', domain=[('state', '=', 'done')])
    marks = fields.Integer(string='Marks')
    student_name = fields.Char("Student Name", reslated='student_id.name')
    reg_no = fields.Char('Reg No', related='student_id.reg_no', store=True)
    roll_no = fields.Integer('Roll No', related='student_id.roll_no', store=True)

class SubjectViewMarkWiz(models.TransientModel):
    _name = "subject.view.marks.wiz"
    _description = "Subject Wise Result"

    exam_id = fields.Many2one("exam.exam", "Exam", help="exam")
    school_id = fields.Many2one("school.school", "School", required=True, help="School of the following standard")
    class_id = fields.Many2one("school.standard")
    section_id = fields.Many2one("standard.division")
    # academic_year_id = fields.Many2one("academic.year", "Academic Year",default=lambda self: self.env['academic.year'].search([('current', '=', True)], limit=1), help="Academic Year")
    # exam_term = fields.Selection([('e1', 'Test 1'), ('e2', 'Test 2'),('e3', 'Test 3'), ('e4', 'Test 4')])
    exam_term = fields.Selection([('e1', 'Half Yearly Exam'), ('e2', 'Final Exam')])
    subject_id = fields.Many2one('subject.subject')
    student_marks_ids = fields.One2many('student.view.marks.line', 'wizard_id', string='Student Marks')

    @api.onchange('class_id')
    def _onchange_class_ids(self):
        all_subjects = self.class_id.mapped('subject_ids')
        print("All subjects =", all_subjects)
        return {'domain': {'subject_id': [('id', 'in', all_subjects.ids)]}}

    @api.onchange('school_id')
    def _onchange_school_id(self):
        self.student_marks_ids = [(5, 0, 0)]

    # @api.onchange('class_id')
    # def _onchange_class_id(self):
    #     if self.class_id:
    #         self.student_marks_ids = [(5, 0, 0)]
    #         students = self.env['student.student'].search([
    #             ('standard_id', '=', self.class_id.id),
    #             ('state', '=', 'done')
    #         ])
    #         lines = []
    #         for student in students:
    #             lines.append((0, 0, {
    #                 'student_id': student.id,
    #                 'marks': 0.0,  # default marks
    #             }))
    #         self.student_marks_ids = lines
    #     else:
    #         self.student_marks_ids = [(5, 0, 0)]  #

    @api.onchange('subject_id')
    def _onchange_subject(self):
        if self.exam_id and self.school_id and self.exam_term and self.class_id:
            self.student_marks_ids = False
            marks = self.env['student.marks'].search([
                ('academic_year_id', '=', self.exam_id.academic_year.id),
                ('subject_id', '=', self.subject_id.id),
                ('standard_id', '=', self.class_id.id),
            ])
            # marline = self.env['student.marks.line'].search([('wizard_id', '=', self.id)])
            print("m=", marks)
            # print("marline=", marline)
            lines = []
            for m in marks:
                lines.append((0, 0, {
                    'student_id': m.student_id.id,
                    'marks':  m.mo1 if self.exam_term == 'e1' else m.mo2
                }))
            self.student_marks_ids = lines

    def add_marks(self):
        print("Add marks.........")
        exam_result_obj = self.env['exam.result']
        student_mark_obj = self.env['student.marks']
        print("ccc", self.student_marks_ids)
        for rec in self.student_marks_ids:
            print("Add Marks.............", rec)
            student_id = rec.student_id
            print("Student=", rec.student_id, rec.roll_no, rec.reg_no)
            exam_result = exam_result_obj.search([
                ('exam_id', '=', self.exam_id.id),
                ('student_id', '=', student_id.id),
                ('class_id', '=', self.class_id.id),
            ])
            if not exam_result:
                exam_result = exam_result_obj.create(
                    {
                        'exam_id': self.exam_id.id,
                        'student_id': student_id.id,
                        'class_id': self.class_id.id,
                        'reg_no': rec.reg_no,
                        'roll_no': rec.roll_no,
                    })
            student_marks = student_mark_obj.search([
                ("exam_result_id", '=', exam_result.id),
                ("subject_id", '=', self.subject_id.id),
            ])
            if not student_marks:
                student_marks = student_mark_obj.create({
                    "exam_result_id": exam_result.id,
                    "subject_id": self.subject_id.id,
                    "student_id": student_id.id,
                    "reg_no": student_id.reg_no,
                    "roll_no": student_id.roll_no,
                    "standard_id": self.class_id.id,
                    "academic_year_id": self.exam_id.academic_year.id
                })
            if self.exam_term == 'e1':
                student_marks.mo1 = rec.marks
            if self.exam_term == 'e2':
                student_marks.mo2 = rec.marks
            # if self.exam_term == 'e3':
            #     student_marks.mo3 = rec.marks
            # if self.exam_term == 'e4':
            #     student_marks.mo4 = rec.marks

    def result_report(self):
        """Method to get the result report"""
        data = self.read()[0]
        return self.env.ref("exam.add_exam_result_id_qweb").report_action([], data=data)

    # def action_print_markslip(self):
    #     print("DDDDDDDDDDDDDDDDDDD")
    #     classes = self.class_ids.ids
    #     data = {
    #         'classes': classes,
    #         'academic_year': self.exam_id.academic_year.name or ''
    #
    #     }
    #     return self.env.ref('up_exam.mark_slip_report_action').report_action(self, data=data)

    # def action_print_markssummary(self):
    #     example_id = self.exam_id
    #     classes = self.class_ids.ids
    #     data = {
    #         # 'print_separate': self.print_separate,
    #         'classes': classes,
    #         'exam': example_id.id
    #     }
    #     return self.env.ref('up_exam.mark_summary_report_action').report_action(self, data=data)

class SubjectViewMarkWizLine(models.TransientModel):
    _name = 'student.view.marks.line'
    _description = 'Subject Result Line'
    _order = 'roll_no asc'

    wizard_id = fields.Many2one('subject.view.marks.wiz', string='Wizard')
    student_id = fields.Many2one('student.student', string='Student')
    marks = fields.Integer(string='Marks')
    student_name = fields.Char("Student Name", reslated='student_id.name')
    reg_no = fields.Char('Reg No', related='student_id.reg_no', store=True)
    roll_no = fields.Integer('Roll No', related='student_id.roll_no', store=True)

class MarkSlip(models.TransientModel):
    _name = 'mark.slip.wiz'
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



    def action_create_mark_slip(self):
        ExamResult = self.env['exam.result']
        Student_marks = self.env['student.marks']

        for wizard in self:
            classes = wizard.class_ids
            print("Classes=", classes)

            for std_class in classes:

                # Get students of class

                students = self.env['student.student'].search([
                    ('standard_id', '=', std_class.id),
                    ('state', '=', 'done')
                ])

                # Get subjects of class
                subjects = std_class.subject_ids
                print("sub-", subjects)

                for student in students:
                    for subject in subjects:
                        # Check if record already exists (avoid duplicates)
                        result_id = ExamResult.search([
                            ('exam_id', '=', wizard.exam_id.id),
                            ('class_id', '=', std_class.id),
                            ('student_id', '=', student.id),
                        ], limit=1)
                        if not result_id:
                            result_id = ExamResult.create(
                                {
                                    'exam_id': wizard.exam_id.id,
                                    'school_id': std_class.school_id.id,
                                    'class_id': std_class.id,
                                    'student_id': student.id,
                                }
                            )

                        student_marks = Student_marks.search([
                            ("exam_result_id", '=', result_id.id),
                            ("subject_id", '=', subject.id),
                            ("student_id", '=', student.id),
                        ])
                        if not student_marks:
                            student_marks = Student_marks.create({
                                "exam_result_id": result_id.id,
                                "subject_id": subject.id,
                                "student_id": student.id,
                                "mo1": 0,
                                "mo2": 0,
                                "t_mo1": self.exam_id.mm1,
                                "t_mo2": self.exam_id.mm2,
                                "total_mark_max": self.exam_id.mm1 + self.exam_id.mm2,
                                "grace_mark": 0,
                                "total_mark": 0,
                            })
                        print("student_marks====", student_marks)
                        # ===================================

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Success"),
                'message': _("Mark slip created successfully."),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_print_markslip(self):
        print("dvvv-----------------")
        classes = self.class_ids.ids
        data = {
            # 'print_separate': self.print_separate,
            'classes': classes,
            'academic_year': self.exam_id.academic_year.name or ''
        }
        return self.env.ref('up_exam.mark_slip_report_action').report_action(self, data=data)

    def action_print_markssummary(self):
        example_id = self.exam_id
        classes = self.class_ids.ids
        data = {
            # 'print_separate': self.print_separate,
            'classes': classes,
            'exam': example_id.id
        }
        return self.env.ref('up_exam.mark_summary_report_action').report_action(self, data=data)









