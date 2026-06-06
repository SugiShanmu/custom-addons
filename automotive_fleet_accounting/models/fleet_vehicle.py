# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    _description = 'Fleet Vehicle Accounting Extension'

    total_maintenance_cost = fields.Monetary(
        string='Total Maintenance Cost',
        currency_field='currency_id',
        compute='_compute_total_cost',
        store=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        readonly=True
    )

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account'
    )

    predicted_monthly_cost = fields.Monetary(
        string='ML Predicted Monthly Cost',
        currency_field='currency_id'
    )
    
    last_prediction_date = fields.Date(string='Last Prediction Date')

    @api.depends('log_services.cost_amount')
    def _compute_total_cost(self):
        for vehicle in self:
            services = self.env['fleet.vehicle.log.services'].search([
                ('vehicle_id', '=', vehicle.id)
            ])
            vehicle.total_maintenance_cost = sum(services.mapped('cost_amount'))

    def action_predict_cost(self):
        return True