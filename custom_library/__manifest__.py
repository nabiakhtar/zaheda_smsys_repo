# See LICENSE file for full copyright and licensing details.

{
    "name": "Library Management for Education ERP",
    "version": "16.0.1.0.0",
    "author": "",
    "category": "School Management",
    "website": "",
    "license": "AGPL-3",
    "summary": "A Module For Library Management For School",
    "complexity": "easy",
    "depends": ["school"],
    "data": [
        "data/library_sequence.xml",
        "security/ir.model.access.csv",
        "views/library_view.xml",
        "wizard/return_book_view.xml",
    ],
    "demo": ["demo/library_demo.xml"],
    # "image": ["static/description/SchoolLibrary.png"],
    "installable": True,
    "application": True,
}
