# See LICENSE file for full copyright and licensing details.

# import time
import calendar
import re

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _

class SubjectSubject(models.Model):
    """Defining a subject"""

    _inherit = "subject.subject"


    exam_in_final = fields.Boolean("Exam in Final")




class SchoolSchool(models.Model):
    """Defining School Information"""

    _inherit = "school.school"
    _description = "School Information"


    result_card_header = fields.Binary(help="Attach Report Card Header")




