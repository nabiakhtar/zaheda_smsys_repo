# See LICENSE file for full copyright and licensing details.

{
    "name": "Exam Management for Education ERP",
    "version": "17.0.1.0.0",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "website": "http://www.serpentcs.com",
    "category": "School Management",
    "license": "AGPL-3",
    "summary": "A Module For Exams Management Taken In School",
    "complexity": "easy",
    "images": ["static/description/Banner_exam_17.png"],
    "depends": ["school"],
    "data": [
        "security/ir.model.access.csv",
        # atr c
        "views/exam_sequence.xml",
        "views/exam_view.xml",
        "views/result_view.xml",
        "views/school_view.xml",
        "wizard/student_marks.xml",
        "wizard/result_build_wiz.xml",
        # "report/report_view.xml"
    ],
    "demo": [],
    "installable": True,
    "application": True,
}
