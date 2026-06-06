# -*- coding: utf-8 -*-
{
    'name': 'Automotive Fleet Accounting Integration',
    'version': '18.0.1.0.0',
    'category': 'Fleet',
    'summary': 'Link Fleet Vehicles with Accounting for Cost Tracking',
    'description': """
        Automotive Fleet Accounting Integration
        * Track total maintenance cost per vehicle
        * Link analytic accounts to fleet vehicles automatically
        * Aggregate invoice/bill costs from accounting
        * Provides base data for ML Analytics module
        * Real-time cost computation on vehicle form
    """,
    'author': 'SugiShanmu',
    'website': 'https://github.com/SugiShanmu/custom-addons',
    'depends': [
        'base',
        'fleet',
        'account',
        'analytic',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_vehicle_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}