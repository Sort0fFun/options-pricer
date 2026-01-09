"""
Pricing API endpoints.
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from backend.services.pricing_service import PricingService
from backend.models.pricing_models import PricingRequest, HeatmapRequest
from pydantic import ValidationError

# Create namespace
ns = Namespace('pricing', description='Option pricing operations')

# API Models for Swagger documentation
pricing_request_model = ns.model('PricingRequest', {
    'futures_price': fields.Float(required=True, description='Current futures price', example=100.0),
    'strike_price': fields.Float(required=True, description='Strike price', example=105.0),
    'days_to_expiry': fields.Integer(required=True, description='Days to expiration', example=30),
    'volatility': fields.Float(required=True, description='Implied volatility (0-1)', example=0.20),
    'risk_free_rate': fields.Float(required=True, description='Risk-free rate (0-1)', example=0.12),
    'option_type': fields.String(description='Option type', example='call', default='call'),
    'contract_symbol': fields.String(description='Contract symbol', example='SCOM'),
    'include_fees': fields.Boolean(description='Include NSE fees', default=False)
})

heatmap_request_model = ns.model('HeatmapRequest', {
    'futures_price': fields.Float(required=True, example=100.0),
    'strike_price': fields.Float(required=True, example=105.0),
    'days_to_expiry': fields.Integer(required=True, example=30),
    'volatility': fields.Float(required=True, example=0.20),
    'risk_free_rate': fields.Float(required=True, example=0.12),
    'price_range_pct': fields.Float(description='Price range %', default=20.0),
    'vol_range_pct': fields.Float(description='Volatility range %', default=50.0),
    'grid_size': fields.Integer(description='Grid size', default=12)
})


@ns.route('/calculate')
class PricingCalculate(Resource):
    """Calculate option prices using Black-76 model."""

    @ns.doc('calculate_option_price')
    @ns.expect(pricing_request_model)
    def post(self):
        """Calculate call and put option prices."""
        try:
            # Validate request
            data = PricingRequest(**request.json)

            # Calculate prices
            result = PricingService.calculate_option_price(
                futures_price=data.futures_price,
                strike_price=data.strike_price,
                days_to_expiry=data.days_to_expiry,
                volatility=data.volatility,
                risk_free_rate=data.risk_free_rate,
                option_type=data.option_type,
                include_fees=data.include_fees
            )

            return {
                'success': True,
                'data': result
            }, 200

        except ValidationError as e:
            return {
                'success': False,
                'message': 'Validation error',
                'errors': e.errors()
            }, 400
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 500


@ns.route('/heatmap')
class PricingHeatmap(Resource):
    """Generate heatmap data for option pricing visualization."""

    @ns.doc('generate_heatmap')
    @ns.expect(heatmap_request_model)
    def post(self):
        """Generate call and put price heatmaps."""
        try:
            # Validate request
            data = HeatmapRequest(**request.json)

            # Generate heatmap
            result = PricingService.generate_heatmap(
                futures_price=data.futures_price,
                strike_price=data.strike_price,
                days_to_expiry=data.days_to_expiry,
                volatility=data.volatility,
                risk_free_rate=data.risk_free_rate,
                price_range_pct=data.price_range_pct,
                vol_range_pct=data.vol_range_pct,
                grid_size=data.grid_size
            )

            return {
                'success': True,
                'data': result
            }, 200

        except ValidationError as e:
            return {
                'success': False,
                'message': 'Validation error',
                'errors': e.errors()
            }, 400
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 500


@ns.route('/contracts')
class PricingContracts(Resource):
    """Get available NSE futures contracts."""

    @ns.doc('get_contracts')
    def get(self):
        """Get list of available contracts."""
        try:
            result = PricingService.get_contracts()
            return {
                'success': True,
                'data': result
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 500
