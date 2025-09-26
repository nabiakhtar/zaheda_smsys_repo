from odoo import models, fields, api




class SelectExamWizard(models.TransientModel):
    _name = 'select.exam.wizard'
    _description = 'Select Exam Wizard'

    # Fields for session, class, and exam
    session_id = fields.Many2one('academic.year', string="Session", )
    class_id = fields.Many2one('school.standard', string="Class", )
    student_id = fields.Many2one('student.student', string="Student",)
    result_id = fields.Many2one('education.exam.results', string='Result Id')
    exam_id = fields.Many2one('education.exam', string='Exam')



    def get_exam_marks1(self):
        session_id = self.session_id
        class_id = self.class_id
        student_id = self.student_id
        exam_id = self.exam_id
        result_id = self.result_id

        domain = [
            # ('academic_year', '=', session_id.id),
            ('class_id', '=', class_id.id),
            ('student_id', '=', student_id.id),
        ]
        marks = self.env['results.subject.line'].search(domain)

        # Create a dictionary to store grouped data
        marks_dic = {}

        # Iterate over the marks and populate the dictionary
        for mark in marks:
            student_name = mark.student_id.name
            subject_name = mark.subject_id.name
            scored_marks = mark.mark_scored
            max_marks = mark.max_mark
            exam_name = mark.exam_id.name

            # Initialize student entry if not already created
            if student_name not in marks_dic:
                marks_dic[student_name] = {}

            # Initialize subject entry if not already created for this student
            if subject_name not in marks_dic[student_name]:
                marks_dic[student_name][subject_name] = []

            # Append the exam marks (scored and max) for the subject
            marks_dic[student_name][subject_name].append({
                'exam_name': exam_name,
                'scored_marks': scored_marks,
                'max_marks': max_marks
            })

        # Format the data for the report
        report_data = []
        for student, subjects in marks_dic.items():
            student_data = {
                'student_name': student,
                'subjects': []
            }
            for subject, exams in subjects.items():
                student_data['subjects'].append({
                    'subject_name': subject,
                    'exams': exams
                })
            report_data.append(student_data)
        print("report_data=", report_data)
        return report_data

    def get_exam_marks(self):
        session_id = self.session_id
        class_id = self.class_id
        student_id = self.student_id
        exam_id = self.exam_id
        result_id = self.result_id

        domain = [
            # ('academic_year', '=', session_id.id),
            ('class_id', '=', class_id.id),
            ('student_id', '=', student_id.id),
        ]
        marks = self.env['results.subject.line'].search(domain)

        # Create a dictionary to store grouped data in the required format
        marks_dic = {}

        # Iterate over the marks and populate the dictionary
        for mark in marks:
            student_name = mark.student_id.name
            subject_name = mark.subject_id.name
            scored_marks = mark.mark_scored
            max_marks = mark.max_mark
            exam_name = mark.exam_id.id

            # Initialize student entry if not already created
            if student_name not in marks_dic:
                marks_dic[student_name] = {}

            # Initialize subject entry for this student if not already created
            if subject_name not in marks_dic[student_name]:
                marks_dic[student_name][subject_name] = {}

            # Append the exam details to the subject dictionary
            exam_key = f"Exam_{exam_name}"  # Dynamic exam key (e.g., 'Exam1', 'Exam2')
            marks_dic[student_name][subject_name][exam_key] = {
                'exam_name': exam_name,
                f'max_mark_{exam_name}': max_marks,
                f'scored_marks_{exam_name}': scored_marks
            }

        # Print the final report data structure (for verification)
        print("marks_dic =", marks_dic)

        return marks_dic

    def generate_report_card(self):
        return self.env.ref('education_exam.report_marks_pdf_action').report_action([], )





