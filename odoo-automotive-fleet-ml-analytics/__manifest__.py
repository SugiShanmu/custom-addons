{
    'name': 'Automotive Fleet ML Analytics',
    'version': '16.0.1.0.0',
    'category': 'Fleet',
    'summary': 'ML-powered Fuel Cost & Maintenance Prediction for Fleet Management',
    'description': """
        Automotive Fleet Management with Machine Learning
        =================================================
        * Predict fuel costs using vehicle history data
        * Forecast maintenance schedules using ML algorithms  
        * Real-time analytics dashboard for fleet managers
        * Integration with GPS tracking and IoT sensors
    """,
    'author': 'SugiShanmu',
    'website': 'https://github.com/SugiShanmu/custom-addons',
    'depends': ['base', 'fleet', 'maintenance', 'mail'],
    'data': [],
    'external_dependencies': {
        'python': ['pandas', 'scikit-learn', 'numpy'],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}