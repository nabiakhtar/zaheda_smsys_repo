{
    'name': 'Transfer Certificate',
    'version': '1.0',
    'category': 'School',
    'summary': 'Manages student transfer certificates',
    'description': 'Generate and manage Transfer Certificates for students.',
    'author': 'Your Name',
    'depends': ['school'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/transfer_certificate_views.xml',
        'report/transfer_certificate_template.xml',
    ],
    'installable': True,
    'application': True,
}
