from email.policy import default

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError



class SchoolSchool(models.Model):
    """Defining School Information"""

    _inherit = "school.school"
    _description = "School Information"


    result_card_header = fields.Binary(help="Attach Report Card Header")