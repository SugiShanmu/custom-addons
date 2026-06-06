from odoo import models, fields, api
from datetime import datetime

class MLPrediction(models.Model):
    _name = 'ml.prediction'
    _description = 'ML Predictions for Fleet Vehicles'
    _order = 'prediction_date desc'
    _rec_name = 'vehicle_id'

    # Link to Vehicle
    vehicle_id = fields.Many2one(
        'fleet.vehicle', 
        string='Vehicle', 
        required=True,
        ondelete='cascade'
    )
    
    # Prediction Details
    prediction_type = fields.Selection([
        ('fuel', 'Fuel Consumption'),
        ('maintenance', 'Maintenance Cost'),
        ('health', 'Vehicle Health Score'),
        ('failure', 'Failure Risk')
    ], string='Prediction Type', required=True)
    
    prediction_date = fields.Datetime(
        string='Prediction Date', 
        default=fields.Datetime.now,
        required=True
    )
    
    # ML Results
    predicted_value = fields.Float(
        string='Predicted Value', 
        digits=(16, 2),
        help="ML model oda output value"
    )
    
    actual_value = fields.Float(
        string='Actual Value', 
        digits=(16, 2),
        help="Real la vandha value. Model accuracy check panna"
    )
    
    confidence_score = fields.Float(
        string='Confidence %', 
        digits=(5, 2),
        help="ML model evlo confident ah iruku - 0 to 100"
    )
    
    # Extra Info
    model_version = fields.Char(
        string='Model Version', 
        default='v1.0',
        help="Edha ML model version use pannom"
    )
    
    input_features = fields.Text(
        string='Input Features Used',
        help="ML ku enna data kuduthom - JSON format la save aagum"
    )
    
    notes = fields.Text(string='Notes')
    
    # For Dashboard
    month = fields.Char(
        string='Month', 
        compute='_compute_month', 
        store=True
    )
    
    @api.depends('prediction_date')
    def _compute_month(self):
        for record in self:
            if record.prediction_date:
                record.month = record.prediction_date.strftime('%Y-%m')
            else:
                record.month = False