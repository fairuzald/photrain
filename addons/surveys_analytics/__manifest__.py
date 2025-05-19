{
    'name': 'Survey Analytics',
    'version': '1.0',
    'summary': 'Analyze survey responses and provide recommendations',
    'author': 'Your Name',
    'category': 'Surveys',
    'depends': ['survey'],
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
    'data': [
        'data/survey_seed_forms.xml',
        'views/survey_analytics_views.xml',
        'views/survey_recommendation_views.xml',
    ],
}
