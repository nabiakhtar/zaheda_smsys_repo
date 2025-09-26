

# See LICENSE file for full copyright and licensing details.

import base64
from odoo.exceptions import UserError, ValidationError
from odoo import _, api, fields, models

try:
    from odoo.tools import image_colorize
except Exception:
    image_colorize = False


class StudentStudent(models.Model):
    """Defining a student information."""

    _inherit = "student.student"



    roll_no = fields.Integer("Roll No.", readonly=False, help="Enter student roll no.")
    registration_date = fields.Date(string="Registration Date")

    def admission_done(self):
        """Method to confirm admission"""
        school_standard_obj = self.env["school.standard"]
        ir_sequence = self.env["ir.sequence"]
        student_group = self.env.ref("school.group_school_student")
        emp_group = self.env.ref("base.group_user")
        for rec in self:
            # if not rec.standard_id:
            #     raise ValidationError(_("Please select class!"))
            # if rec.standard_id.remaining_seats < 0:
            #     raise ValidationError(
            #         _("Seats of class %s are full") % rec.standard_id.standard_id.name
            #     )
            domain = [("school_id", "=", rec.school_id.id)]
            # Checks the standard if not defined raise error
            # if not school_standard_obj.search(domain):
            #     raise UserError(_("Warning! The standard is not defined in school!"))
            # Assign group to student
            rec.user_id.write({"groups_id": [(6, 0, [emp_group.id, student_group.id])]})
            # Assign roll no to student
            number = 1
            # ======= custom ===============
            # for rec_std in rec.search(domain):
            #     rec_std.roll_no = number
            #     number += 1
            # =================================
            # Assign registration code to student
            reg_code = ir_sequence.next_by_code("student.registration")
            registation_code = (
                    str(rec.school_id.state_id.name)
                    + str("/")
                    + str(rec.school_id.city)
                    + str("/")
                    + str(rec.school_id.name)
                    + str("/")
                    + str(reg_code)
            )
            stu_code = ir_sequence.next_by_code("student.code")
            student_code = (
                    str(rec.school_id.code)
                    + str("/")
                    + str(rec.year.code)
                    + str("/")
                    + str(stu_code)
            )
            rec.write(
                {
                    "state": "done",
                    "admission_date": fields.Date.today(),
                    "student_code": student_code,
                    "reg_code": registation_code,
                }
            )
            # template = (
            #     self.env["mail.template"]
            #     .sudo()
            #     .search([("name", "ilike", "Admission Confirmation")], limit=1)
            # )
            # if template:
            #     for user in rec.parent_id:
            #         subject = _("About Admission Confirmation")
            #         if user.email:
            #             body = (
            #                     """
            #                 <div>
            #                     <p>Dear """
            #                     + str(user.display_name)
            #                     + """,
            #                 <br/><br/>
            #                 Admission of """
            #                     + str(rec.display_name)
            #                     + """ has been confirmed in """
            #                     + str(rec.school_id.name)
            #                     + """.
            #                 <br></br>
            #                 Thank You.
            #             </div>
            #             """
            #             )
            #             template.send_mail(
            #                 rec.id,
            #                 email_values={
            #                     "email_from": self.env.user.email or "",
            #                     "email_to": user.email,
            #                     "subject": subject,
            #                     "body_html": body,
            #                 },
            #                 force_send=True,
            #             )
        return True