# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AssignRollNo(models.TransientModel):
    """designed for assigning roll number to a student"""

    _name = "assign.roll.no"
    _description = "Assign Roll Number"

    school_id = fields.Many2one('school.school', string='School')
    # standard_id = fields.Many2one("school.standard", "Class", required=True)
    class_ids = fields.Many2many(
        'school.standard',
        string="Classes",
        domain="[('school_id', '=', school_id)]"
    )
    sort_by = fields.Selection([('n', 'Name'), ('rg', 'RegNo'), ('ad', 'Admission Date')], default='n')


    def assign_rollno(self):
        """Method to assign roll no to students"""
        student_obj = self.env["student.student"]
        # Search Student

        sort_by = 'name'
        if self.sort_by == 'rg':
            sort_by = 'reg_no'
        if self.sort_by == 'ad':
            sort_by = 'admission_date'

        for rec in self:
            # Assign roll no according to name.
            classes = rec.class_ids
            number = 1
            for std_class in classes:
                for student in student_obj.search(
                        [
                            ("standard_id", "=", std_class.id),
                            ("state", "=", 'done'),
                        ],
                        order=sort_by,
                ):
                    student.write({"roll_no": number})
                    number += 1
