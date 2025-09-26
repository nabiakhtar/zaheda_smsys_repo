import datetime

from odoo import models, fields, api
import pandas as pd
import base64
from io import BytesIO

from odoo.exceptions import UserError


class PartnerImport(models.TransientModel):
    _name = 'partner.import'
    _description = 'Import Partners from Excel'

    file = fields.Binary('Excel File', required=True)
    filename = fields.Char('File Name')

    def import_data(self):
        """Imports the Excel data into the res.partner model."""
        # Step 1: Decode the file (it comes in as base64 from the form)
        file_data = base64.b64decode(self.file)
        excel_file = BytesIO(file_data)

        # Step 2: Read the Excel file using pandas
        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            raise UserError(f"Error reading the Excel file: {str(e)}")

        # Step 3: Process each row in the Excel file and import data into res.partner
        for index, row in df.iterrows():
            try:
                RegNo = row.get('RegNo')
                StudName = row.get('StudName')
                Sex = row.get('Sex')
                dd = row.get('dd')
                mm = row.get('mm')
                yy = row.get('yy')

                dob = str(mm) + "/" + str(dd) + "/"  + str(yy)
                dob_date = datetime.datetime.strptime(dob, '%m/%d/%Y')
                contact = row.get('Contact')
                FName = row.get('FName')
                Address = row.get('Address')
                PrevoiusSchool = row.get('PrevoiusSchool')
                Class = row.get('Class')
                dd1 = row.get('dd1')
                mm1 = row.get('mm1')
                yy1 = row.get('yy1')
                doa =  str(mm1) + "/" + str(dd1) + "/"  + str(yy1)
                doa_date = datetime.datetime.strptime(doa, '%m/%d/%Y')

                student_data = {
                    'reg_no': RegNo,
                    'name': StudName,
                    'date_of_birth': dob_date,
                    'contact_mobile': contact,
                    'father_name': FName,
                    'street': Address,
                    'country_id': 104,
                    'city': 'اعظم گڈھ',
                    'remark': str(PrevoiusSchool)+ "," + str(Class) ,
                    'school_id': 1,
                    'state_id': 610,
                    'admission_date': doa_date,
                    # 'medium_id': 1,
                    # 'standard_id': 1,
                    # 'division_id': 1,
                    'mobile': contact,
                    'year': 1
                }
                print("Index====", index, student_data )

                self.env['student.student'].create(student_data)
            except Exception as  e:
                print("Record Not created for ", RegNo)
                print("error", e)
        return True
