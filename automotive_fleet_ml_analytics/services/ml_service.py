from odoo import api, models
from datetime import datetime, timedelta
import json
import random

class MLService(models.AbstractModel):
    _name = 'ml.service'
    _description = 'ML Service for Fleet Predictions'

    # 1. FUEL CONSUMPTION PREDICTION
    @api.model
    def predict_fuel_consumption(self, vehicle_id):
        """
        Logic: Last 3 month avg + Vehicle age factor + Random variation
        """
        vehicle = self.env['fleet.vehicle'].browse(vehicle_id)
        # Step 1: Last 3 month fuel data edukuradhu
        three_months_ago = datetime.now() - timedelta(days=90)
        fuel_logs = self.env['fleet.vehicle.log.fuel'].search([
            ('vehicle_id', '=', vehicle_id),
            ('date', '>=', three_months_ago)
        ])       
        # Step 2: Average mileage calculate 
        if fuel_logs:
            total_km = sum(fuel_logs.mapped('odometer')) 
            total_liter = sum(fuel_logs.mapped('liter'))
            avg_mileage = total_km / total_liter if total_liter else 12.0
        else:
            avg_mileage = 12.0  # Default value
        # Step 3: Vehicle age factor
        if vehicle.acquisition_date:
            age_years = (datetime.now().date() - vehicle.acquisition_date).days / 365
            age_factor = max(0.7, 1 - (age_years * 0.03))  # Year ku 3% kammi
        else:
            age_factor = 1.0
        # Step 4: Final prediction
        predicted_mileage = round(avg_mileage * age_factor * random.uniform(0.95, 1.05), 2)
        confidence = random.uniform(85, 95)  # 85-95% confident    
        # Step 5: Input features save 
        input_data = {
            'avg_mileage_3m': round(avg_mileage, 2),
            'age_factor': round(age_factor, 2),
            'vehicle_age_years': round(age_years, 1) if vehicle.acquisition_date else 0,
            'fuel_logs_count': len(fuel_logs)
        }
        # Step 6:
        self.env['ml.prediction'].create({
            'vehicle_id': vehicle_id,
            'prediction_type': 'fuel',
            'predicted_value': predicted_mileage,
            'confidence_score': confidence,
            'model_version': 'v1.0-basic',
            'input_features': json.dumps(input_data)
        })
        
        return {
            'vehicle': vehicle.name,
            'predicted_mileage': predicted_mileage,
            'confidence': round(confidence, 1),
            'message': f'{vehicle.name} ku next month {predicted_mileage} km/l varum'
        }

    # 2. MAINTENANCE COST PREDICTION
    @api.model
    def predict_maintenance_cost(self, vehicle_id):
        """
        Next month maintenance cost predict pannum
        Logic: Last 6 month avg cost + KM factor + Age factor
        """
        vehicle = self.env['fleet.vehicle'].browse(vehicle_id)
        
        # Step 1: Last 6 month cost data
        six_months_ago = datetime.now() - timedelta(days=180)
        costs = self.env['fleet.vehicle.log.services'].search([
            ('vehicle_id', '=', vehicle_id),
            ('date', '>=', six_months_ago)
        ])
        
        avg_monthly_cost = sum(costs.mapped('amount')) / 6 if costs else 3000.0
        
        # Step 2: High KM na cost adhigam aagum
        km_factor = 1.0
        if vehicle.odometer > 100000:
            km_factor = 1.3  # 30% extra
        elif vehicle.odometer > 50000:
            km_factor = 1.15  # 15% extra
            
        predicted_cost = round(avg_monthly_cost * km_factor * random.uniform(0.9, 1.1), 2)
        confidence = random.uniform(80, 92)
        
        input_data = {
            'avg_monthly_cost_6m': round(avg_monthly_cost, 2),
            'km_factor': km_factor,
            'current_odometer': vehicle.odometer,
            'services_count_6m': len(costs)
        }
        
        self.env['ml.prediction'].create({
            'vehicle_id': vehicle_id,
            'prediction_type': 'maintenance',
            'predicted_value': predicted_cost,
            'confidence_score': confidence,
            'model_version': 'v1.0-basic',
            'input_features': json.dumps(input_data)
        })
        
        return {
            'vehicle': vehicle.name,
            'predicted_cost': predicted_cost,
            'confidence': round(confidence, 1),
            'message': f'{vehicle.name} ku next month ₹{predicted_cost} maintenance varum'
        }

    # 3. VEHICLE HEALTH SCORE
    @api.model
    def calculate_health_score(self, vehicle_id):
        """
        Vehicle health ah 0-100 score kudukum
        Logic: Mileage score + Service score + Age score
        """
        vehicle = self.env['fleet.vehicle'].browse(vehicle_id)
        score = 100  # Full mark la start pannuvom
        
        # Factor 1: Mileage - High KM means score less
        if vehicle.odometer > 150000:
            score -= 30
        elif vehicle.odometer > 100000:
            score -= 20
        elif vehicle.odometer > 50000:
            score -= 10
            
        # Factor 2: Last service ? 6 month 
        last_service = self.env['fleet.vehicle.log.services'].search([
            ('vehicle_id', '=', vehicle_id)
        ], order='date desc', limit=1)
        
        if last_service:
            days_since_service = (datetime.now().date() - last_service.date).days
            if days_since_service > 180:  # 6 months
                score -= 25
            elif days_since_service > 90:  # 3 months
                score -= 10
        else:
            score -= 15  # Service eh pannala
            
        # Factor 3: Vehicle age
        if vehicle.acquisition_date:
            age_years = (datetime.now().date() - vehicle.acquisition_date).days / 365
            if age_years > 10:
                score -= 20
            elif age_years > 5:
                score -= 10
                
        final_score = max(0, min(100, round(score, 1)))  # 0-100 kulla irukanum
        
        # Health status
        if final_score >= 80:
            status = 'Excellent'
        elif final_score >= 60:
            status = 'Good'
        elif final_score >= 40:
            status = 'Average'
        else:
            status = 'Poor - Needs Attention'
            
        input_data = {
            'odometer': vehicle.odometer,
            'days_since_last_service': days_since_service if last_service else 'Never',
            'vehicle_age_years': round(age_years, 1) if vehicle.acquisition_date else 0
        }
        
        self.env['ml.prediction'].create({
            'vehicle_id': vehicle_id,
            'prediction_type': 'health',
            'predicted_value': final_score,
            'confidence_score': 100,  # Formula based, so 100% confident
            'model_version': 'v1.0-basic',
            'input_features': json.dumps(input_data)
        })
        
        return {
            'vehicle': vehicle.name,
            'health_score': final_score,
            'status': status,
            'message': f'{vehicle.name} Health Score: {final_score}/100 - {status}'
        }

    # 4. RUN ALL PREDICTIONS FOR ONE VEHICLE
    @api.model
    def run_all_predictions(self, vehicle_id):
        """Oru vehicle ku 3 prediction um run pannum"""
        fuel = self.predict_fuel_consumption(vehicle_id)
        cost = self.predict_maintenance_cost(vehicle_id)
        health = self.calculate_health_score(vehicle_id)
        
        return {
            'fuel': fuel,
            'maintenance': cost,
            'health': health
        }