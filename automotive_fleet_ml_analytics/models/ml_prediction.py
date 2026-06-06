from odoo import models, fields, api
from datetime import datetime
from logging 


_logger = logging.getLogger(__name__)
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
    
class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    _description = 'Fleet Vehicle ML Extensions'

    def action_predict_fuel(self):
        """Predict Fuel button action in vehicle form"""
        self.ensure_one()
        result = self.env['ml.service'].predict_fuel_consumption(self.id)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Fuel Prediction Success',
                'message': f"Predicted Mileage: {result['predicted_mileage']} km/l\nConfidence: {result['confidence']*100:.0f}%",
                'type': 'success',
                'sticky': False,
            }
        }

    def action_predict_maintenance(self):
        """Predict Maintenance button action in vehicle form"""
        self.ensure_one()
        result = self.env['ml.service'].predict_maintenance_days(self.id)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Maintenance Prediction',
                'message': f"Next Service in: {result['predicted_days']} days\nConfidence: {result['confidence']*100:.0f}%",
                'type': 'success',
                'sticky': False,
            }
        }

    def action_predict_health(self):
        """Predict Health button action in vehicle form"""
        self.ensure_one()
        result = self.env['ml.service'].predict_vehicle_health(self.id)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Health Prediction',
                'message': f"Vehicle Health Score: {result['predicted_health']}/100\nConfidence: {result['confidence']*100:.0f}%",
                'type': 'success',
                'sticky': False,
            }
        }

    @api.model
    def action_cron_predict_fuel_all(self):
        """Cron: Daily fuel prediction for all vehicles"""
        vehicles = self.search([])
        for vehicle in vehicles:
            try:
                self.env['ml.service'].predict_fuel_consumption(vehicle.id)
            except Exception as e:
                _logger.error(f"ML Cron failed for vehicle {vehicle.name}: {e}")
        _logger.info(f"ML: Daily Fuel Prediction Cron Completed for {len(vehicles)} vehicles")
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