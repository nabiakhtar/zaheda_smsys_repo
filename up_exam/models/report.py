# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class Markslip(models.AbstractModel):
	_name = 'report.up_exam.report_markslip'
	_description = 'Markslip Report'



	@api.model
	def _get_report_values(self, docids, data=None):
		# data = self.get_subject_summary_by_class()
		# return self.env.ref('your_module.subject_summary_report').report_action(self, data=data)

		report1 = self.env['ir.actions.report']._get_report_from_name('up_exam.report_markslip')
		if data:
			print("Data=", data)
			if data.get('classes'):
				clases = self.env['school.standard'].browse(data.get('classes'))
				print("Class=", clases)
			if data.get('academic_year'):
				academic_year = data.get('academic_year')
			if data.get('school_name'):
				school_name = data.get('school_name')
			if data.get('school_address'):
				school_address = data.get('school_address')

		return {
			'doc_ids': self.ids,
			'doc_model': report1.model,
			'docs': clases,
			'academic_year': academic_year,
			'school_name': school_name,
			'school_address': school_address,
		}


class MarkSummaryReport(models.AbstractModel):
	_name = 'report.up_exam.report_markssummary'
	_description = 'Markslip Report'



	@api.model
	def _get_report_values(self, docids, data=None):
		report1 = self.env['ir.actions.report']._get_report_from_name('up_exam.report_markssummary')
		print("Report , ", report1)
		print("data , ", data)
		if data and data.get('classes') and data.get('exam'):
			clases = self.env['school.standard'].browse(data.get('classes'))
			print("Class=", clases)


		return {
			'doc_ids': self.ids,
			'doc_model': report1.model,
			'exam': data.get('exam'),
			'docs': clases,

		}

