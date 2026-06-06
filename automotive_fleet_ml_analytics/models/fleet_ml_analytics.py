# -*- coding: utf-8 -*-
from odoo import models, fields

 class FleetMLAnalytics(models.Model):
    """Model to store ML Analytics predictions for fleet vehicles."""
    _name = 'automotive.fleet.ml.analytics'
    _description = 'Automotive Fleet ML Analytics'

    name = fields.Char(string='Reference', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    prediction_score = fields.Float(string='ML Prediction Score')
    prediction_date = fields.Datetime(string='Prediction Date')