from odoo import models, fields, api




class SelectExamWizard(models.TransientModel):
    _name = 'select.exam.wizard'
    _description = 'Select Exam Wizard'

    # Fields for session, class, and exam
    session_id = fields.Many2one('academic.year', string="Session", )
    class_id = fields.Many2one('school.standard', string="Class", )
    student_id = fields.Many2one('student.student', string="Student",)
    result_id = fields.Many2one('education.exam.results', string='Result Id')
    exam_id1 = fields.Many2one('education.exam', string='Exam', domain=[('state', '=', 'ongoing')])
    exam_id2 = fields.Many2one('education.exam', string='Exam Final', domain=[('state', '=', 'ongoing')])




    def build_students_marks(self):
        exam_id1 = self.exam_id1
        exam_id2 = self.exam_id2
        result_id = self.result_id
        domain = [
            ('exam_id', '=', exam_id2.id),
        ]
        marks = self.env['results.subject.line'].search(domain)
        # Iterate over the marks and populate the dictionary
        for mark in marks:
            mark1 = self.env['results.subject.line'].search([
                ('student_id', '=',mark.student_id.id),
                ('subject_id', '=',mark.subject_id.id),
                ('exam_id', '=',exam_id1.id),
            ])
            mark.mark_scored_e1 = mark1.mark_scored
            if mark.subject_id.exam_in_final:
                mark.max_mark_e1 = 0
            else:
                mark.max_mark_e1 = mark1.max_mark

            mark.mark_scored_e2 = mark.mark_scored
            mark.max_mark_e2 = mark.max_mark
        # print("Exam id =",self.exam_id2)
        # result_id = self.env['education.exam.results'].search([('result_id', '=', 78)])
        # print("exam_id2.....",result_id)
        # sadsad
        #


        # calculate result
        # exam_id2.cal_result()
        # exam_id2.cal_student_position()









    def generate_report_card(self):
        return self.env.ref('education_exam.report_marks_pdf_action').report_action([], )
