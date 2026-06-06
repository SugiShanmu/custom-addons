# -*- coding: utf-8 -*-
{
    'name': 'Automotive Fleet ML Analytics',
    'version': '16.0.1.0.0',
    'category': 'Fleet',
    'summary': 'ML-powered Fuel Cost & Maintenance Prediction with Accounting Integration',
    'description': """
        Automotive Fleet Management with Machine Learning
        * Predict fuel costs using vehicle history data
        * Forecast maintenance schedules using ML algorithms
        * Real-time analytics dashboard for fleet managers
        * Accounting integration for cost prediction
        * Uses analytic accounts and invoice data for better ML
    """,
    'author': 'SugiShanmu',
    'website': 'https://github.com/SugiShanmu/custom-addons',
    'depends': [
        'base',
        'fleet',
        'maintenance',
        'mail',
        'automotive_fleet_accounting',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_vehicle_views.xml',
        'views/ml_dashboard_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'automotive_fleet_ml_analytics/static/src/js/dashboard.js',
            'automotive_fleet_ml_analytics/static/src/css/dashboard.css'
        ],
    },
    'external_dependencies': {
        'python': ['pandas', 'scikit-learn', 'numpy', 'joblib'],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}