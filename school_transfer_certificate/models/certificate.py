from vobject import readOne

from odoo import models, fields, api
from datetime import date

class SchoolTransferCertificate(models.Model):
    _name = 'school.transfer.certificate'
    _description = 'Student Transfer Certificate'
    _order = 'issue_date desc'

    name = fields.Char(string="TC Number", required=True, copy=False, readonly=True,
                       default=lambda self: 'New')
    student_id = fields.Many2one('student.student', string='Student', required=True)
    en_student_name = fields.Char(related='student_id.en_name')
    # admission_no = fields.Char(related='student_id.admission_no', string='Admission No', readonly=True)
    reg_no = fields.Char(related='student_id.reg_no', string='Registration No', readonly=True, store=True)
    standard_id = fields.Many2one("school.standard",related='student_id.standard_id', string='Class',store=True, readonly=True)
    father_name = fields.Char(related='student_id.father_name', string="Father's Name", readonly=True)
    mother_name = fields.Char(related='student_id.mother_name', string="Mother's Name", readonly=True)
    en_mother_name = fields.Char(related='student_id.en_mother_name',  readonly=True)
    en_father_name = fields.Char(related='student_id.en_father_name', string="Father's Name", readonly=True)
    en_address = fields.Char(string="Address")
    issue_date = fields.Date(string='Issue Date', default=date.today())
    reason = fields.Text(string='Reason for Leaving')
    leave_date = fields.Date("Leave Date")
    next_class_id = fields.Many2one('standard.standard')
    fail_pass = fields.Char("Student is passed or failed")
    last_exam_date = fields.Date("Last Exam Date")
    fee_paid = fields.Selection([('yes', 'YES'), ('no', 'NO')])
    cast_id = fields.Many2one(
        "student.cast", "Religion/Caste", help="Select student cast", related='student_id.cast_id', store=True, readonly=False
    )

    registration_date = fields.Date(string="Registration Date", related="student_id.registration_date",store=True, readonly=False)
    en_class = fields.Char("Class -English")

    en_section = fields.Char("Section -English")
    en_last_class = fields.Char("Last Class -English")

    division_id = fields.Many2one(
        "standard.division",
        "Division",
        help="Select student standard division",
        related="student_id.division_id",
        store=False,
        readonly=False
    )

    character = fields.Char()
    remarks = fields.Text(string='Remarks')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('school.transfer.certificate') or 'New'
        return super().create(vals)

    def action_issue(self):
        for rec in self:
            rec.state = 'issued'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'



class SchoolSchool(models.Model):
    """Defining School Information"""

    _inherit = "school.school"
    _description = "School Information"


    tc_header = fields.Binary(help="Attach TC Header", string="TC Header")
