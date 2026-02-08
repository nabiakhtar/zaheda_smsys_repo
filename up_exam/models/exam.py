from email.policy import default

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ExamExam(models.Model):
    """Defining model for Exam."""

    _name = "exam.exam"
    _description = "Exam Information"


    active = fields.Boolean(default="True", help="Activate/Deactivate record")
    name = fields.Char(string="Exam Name", required=True, help="Name of Exam")
    exam_code = fields.Char(readonly=True, help="Code of exam")
    standard_id = fields.Many2many(
        "standard.standard",
        "standard_standard_exam_rel",
        "standard_id",
        "event_id",
        "Participant Standards",
        help="Select Standard",
    )
    start_date = fields.Date("Exam Start Date", help="Exam will start from this date")
    end_date = fields.Date("Exam End date", help="Exam will end at this date")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("running", "Running"),
            ("finished", "Finished"),
            ("cancelled", "Cancelled"),
        ],
        readonly=True,
        default="draft",
        help="State of the exam",
    )
    grade_system = fields.Many2one("grade.master", help="Select Grade System")
    academic_year = fields.Many2one("academic.year", help="Select Academic Year")
    # exam_schedule_ids = fields.One2many(
    #     "exam.schedule.line",
    #     "exam_id",
    #     "Exam Schedule",
    #     help="Enter exam schedule",
    # )

    # ================= custom =====================
    school_id = fields.Many2one('school.school', 'School')
    all_sub_exam_mark = fields.Integer("Total Marks", default=100)
    coordinator_id = fields.Many2one('hr.employee', "Exam Coordinator")
    exam_term_ids = fields.Many2many('exam.term')
    exam_subject_ids = fields.Many2many('subject.subject')
    e1 = fields.Char("First Exam")
    e2 = fields.Char("Second Exam")
    e3 = fields.Char("Third Exam")
    e4 = fields.Char("Final Exam")

    mm1 = fields.Integer("Max Mark", default=50)
    mm2 = fields.Integer("Max Mark", default=50)
    mm3 = fields.Integer("Max Mark", default=10)
    mm4 = fields.Integer("Max Mark", default=50)

    pm1 = fields.Integer("Passing Mark", default=0)
    pm2 = fields.Integer("Passing Mark", default=0)
    pm3 = fields.Integer("Passing Mark", default=0)
    pm4 = fields.Integer("Passing Mark", default=0)

    hye_gm = fields.Integer(string="HEY Grace Mark", default=10)
    fe_gm = fields.Integer(string="FE Grace Mark", default=20)

    # ==============================================
    # ==============================================

    @api.model
    def create(self, vals):
        vals["exam_code"] = self.env["ir.sequence"].next_by_code("exam.exam") or _(
            "New"
        )
        return super().create(vals)

    def set_to_draft(self):
        """Method to set state to draft"""
        self.state = "draft"

    def set_running(self):
        """Method to set state to running"""
        for rec in self:
            if not rec.standard_id:
                raise ValidationError(_("Please Select Standard!"))
            rec.state = "running"

    def set_finish(self):
        """Method to set state to finish"""
        self.state = "finished"

    def set_cancel(self):
        """Method to set state to cancel"""
        self.state = "cancelled"

class ExamTerm(models.Model):
    _name = 'exam.term'
    _description = "Exam term"


    exam_id = fields.Many2one("exam.exam", "Exam", help="exam")
    name = fields.Char(string="Exam Term", required=True, help="Exam Term")
    hi_name = fields.Char(string="परीक्षा अवधि", required=True, help="परीक्षा अवधि")
    max_mark = fields.Integer("Max Mark", required=True)
    passing_marks = fields.Integer("Passing Marks", required=True)
    start_date = fields.Date("Exam Start Date", help="Exam will start from this date")
    end_date = fields.Date("Exam End date", help="Exam will end at this date")
    running = fields.Boolean()
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("running", "Running"),
            ("finished", "Finished"),
            ("cancelled", "Cancelled"),
        ],
        readonly=True,
        default="draft",
        help="State of the exam",
    )

class ExamStudentMarks(models.Model):
    _name = 'student.marks'
    _rec_name = 'exam_result_id'

    exam_result_id = fields.Many2one('exam.result')
    student_id = fields.Many2one("student.student")
    reg_no = fields.Char("Reg No")
    roll_no = fields.Integer("Roll No")
    subject_id = fields.Many2one("subject.subject")
    standard_id = fields.Many2one("school.standard")
    academic_year_id = fields.Many2one("academic.year", "Academic Year", help="Academic Year")
    mo1 = fields.Integer("HEY Obtain")
    mo2 = fields.Integer("FE Obtain")
    t_mo2 = fields.Integer("FE Maz")
    t_mo1 = fields.Integer("HYE Max")
    grace_mark = fields.Integer("Grace Marks")
    total_mark_max = fields.Integer("Total Max")
    total_mark = fields.Integer("Total")

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Confirm"),
            ("re-evaluation", "Re-Evaluation"),
            ("re-evaluation_confirm", "Re-Evaluation Confirm"),
        ],
        readonly=True,
        tracking=True,
        default="draft",
        help="State of the exam",
    )

    # @api.depends('mo1', 'mo2', 'grace_mark')
    # def _cal_total(self):
    #     self.total_mark = 0
    #     for rec in self:
    #         rec.total_mark = rec.mo1 +rec.mo2 + rec.grace_mark


    def write(self, vals):
        print("Write====", vals)
        result = super(ExamStudentMarks, self).write(vals)
        if 'mo1' in vals or 'mo2' in vals:
            if result:
                standard_id = self.standard_id
                student_results = self.env['exam.result'].search([('class_id', '=', standard_id.id)])
                print("Stufent=", student_results)
                if student_results:
                    for sr in student_results:
                        sr.is_cald = False
                        sr.state = 'draft'
        return result


    @api.depends('mo1', 'mo2')
    def _cal_grace_mark(self):
        passing_marks = 34
        grace_max_marks = 20
        remain_grace_mark = grace_max_marks
        sorted_records = sorted(self, key=lambda record: record.mo1 + record.mo2, reverse=True)
        print("Sored ", sorted_records)
        total_grace_added = 0
        total_marks_obtained = 0
        self.grace_mark = 0

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

class ExamResult(models.Model):
    _name = 'exam.result'
    _rec_name = 'student_id'


    exam_id = fields.Many2one("exam.exam", "Exam", help="exam")
    school_id = fields.Many2one('school.school')
    # academic_year_id = fields.Many2one("academic.year", "Academic Year", help="Academic Year")
    admission_no = fields.Char()
    reg_no = fields.Char("Registration No", related="student_id.reg_no")
    student_id = fields.Many2one("student.student")
    student_name = fields.Char("Student Name", related=student_id.name ,store=True)
    mother_name = fields.Char(related="student_id.mother_name")
    father_name = fields.Char(related="student_id.father_name")
    attendance_e1 = fields.Integer()
    attendance_e2 = fields.Integer()
    attendance_et1 = fields.Integer()
    attendance_et2 = fields.Integer()

    roll_no = fields.Integer(related='student_id.roll_no')
    # class_name = fields.Char(related=student_id.standard_id.name, store=True)
    class_id = fields.Many2one("school.standard", related="student_id.standard_id", store=True)
    dob = fields.Date(related="student_id.date_of_birth", store=True)
    contact_no = fields.Char(related='student_id.mobile', store=True)
    total_grace_mark = fields.Integer(string='Total Grace Mark')

    position = fields.Integer()
    division = fields.Char()

    is_cald = fields.Boolean(readonly=1)
    is_printed = fields.Boolean(readonly=1)

    total_max = fields.Integer(
        string="Total Max",
        store=True,
        help="Total of Max Marks",
    )

    total = fields.Integer(
        string="Obtain Total",
        store=True,
        help="Total of marks",
    )
    percentage = fields.Float(
        store=True,
        help="Percentage Obtained",
    )
    result = fields.Char(
        store=True,
        help="Result Obtained",
    )
    grade = fields.Char( store=True, help="Grade Obtained")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Confirm"),
            ("re-evaluation", "Re-Evaluation"),
            ("re-evaluation_confirm", "Re-Evaluation Confirm"),
        ],
        readonly=True,
        tracking=True,
        default="draft",
        help="State of the exam",
    )
    color = fields.Integer(help="Color")
    active = fields.Boolean(default=True, help="Activate/Deactivate record")
    grade_system = fields.Many2one("grade.master", help="Grade System selected")
    student_marks_ids = fields.One2many("student.marks", "exam_result_id", "Marks", help="Student Marks")


    def cal_result(self):
        PASS_MARK = 33
        TOTAL_GRACE = 20

        for s in self:
            if not s.is_cald:

                total = 0
                total_max = 0
                tgrm = 0
                remaining_grace = TOTAL_GRACE

                # Sort by lowest marks first (weaker subjects first)
                sorted_subjects = s.student_marks_ids.sorted(
                    key=lambda rec: rec.mo1 + rec.mo2, reverse=True
                )

                # -----------------------------------------
                # 1️⃣ CALCULATE GRACE, TOTAL MARKS, PERCENTAGE
                # -----------------------------------------
                for rec in sorted_subjects:
                    mark = rec.mo1 + rec.mo2
                    rec.grace_mark = 0

                    if mark < PASS_MARK and remaining_grace > 0:
                        required = PASS_MARK - mark
                        given = min(required, remaining_grace)
                        tgrm += given
                        rec.grace_mark = given
                        remaining_grace -= given

                    rec.total_mark = mark + rec.grace_mark
                    total += rec.total_mark
                    total_max += rec.total_mark_max

                # Store student total & percentage
                subjects = len(s.student_marks_ids)
                s.total = total
                s.total_max = total_max
                s.percentage = round(total / total_max * 100, 2) if subjects else 0
                s.total_grace_mark = tgrm

                # -----------------------------------------
                # 2️⃣ DETERMINE RESULT STATE
                # -----------------------------------------

                count_below_34 = len(
                    list(filter(lambda mark: mark < 33, s.student_marks_ids.mapped('total_mark'))))
                print("CCC=", count_below_34)
                result = 'کامیاب'
                if count_below_34 == 1:
                    result = 'ترقی'
                if count_below_34 == 2:
                    result = 'ضمنی'
                if count_below_34 >= 3:
                    result = 'نا کام'
                s.result = result

                s.division = self.cal_division(s.percentage)

                s.is_cald = True
                s.state = "confirm"

                # -----------------------------------------
                # 3️⃣ DIVISION Only if Passed & NO grace
                # -----------------------------------------


        # -----------------------------------------
        # 4️⃣ ASSIGN CLASS POSITION (Rank)
        # -----------------------------------------
        # all students of the class
        class_students = self.search([
            ('class_id', '=', self.class_id.id),
            ('is_cald', '=', True)
        ])

        # eligible for ranking = NO grace + passed all subjects
        eligible = class_students.filtered(
            lambda st: st.result == "کامیاب" and st.total_grace_mark == 0).sorted(key=lambda st: st.percentage, reverse=True)

        # Assign rank
        position = 1
        for st in eligible:
            st.position = position
            position += 1

        # Non-eligible get no position
        for st in class_students - eligible:
            st.position = False
            st.division = False

    def re_cal_result(self):
        self.state = 'draft'
        self.is_cald = False

    def cal_division(self, percentage):
        if percentage:
            if percentage > 59:
                return "I"
            if percentage > 49:
                return "II"
            return "III"
        return ''


    # one time use
    def update_marks1(self):
        for rec in self.search([]):
            for c in rec.student_marks_ids:
                if not c.student_id:
                    c.standard_id = rec.class_id.id
                    c.student_id = rec.student_id.id
                    c.reg_no = rec.reg_no
                    c.roll_no = rec.roll_no













