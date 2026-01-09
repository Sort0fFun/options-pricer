"""
PnL API endpoints.
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from backend.services.pnl_service import PnLService
from backend.models.pnl_models import AnalyzeRequest, StrategyBuilderRequest
from pydantic import ValidationError

# Create namespace
ns = Namespace('pnl', description='P&L analysis and strategy operations')

# API Models for Swagger documentation
strategy_leg_model = ns.model('StrategyLeg', {
    'option_type': fields.String(required=True, description='call or put', example='call'),
    'strike': fields.Float(required=True, description='Strike price', example=100.0),
    'premium': fields.Float(required=True, description='Option premium', example=5.0),
    'quantity': fields.Integer(description='Number of contracts', default=1),
    'position_type': fields.String(description='long or short', default='long')
})

market_params_model = ns.model('MarketParams', {
    'current_price': fields.Float(required=True, example=100.0),
    'price_range_pct': fields.Float(default=50, example=50),
    'time_to_expiry': fields.Float(default=0.0822, example=0.0822)
})

analyze_request_model = ns.model('AnalyzeRequest', {
    'strategy': fields.Nested(ns.model('StrategyConfig', {
        'legs': fields.List(fields.Nested(strategy_leg_model))
    })),
    'market_params': fields.Nested(market_params_model)
})

strategy_builder_model = ns.model('StrategyBuilder', {
    'strategy_name': fields.String(required=True, example='long_call'),
    'parameters': fields.Raw(required=True, description='Strategy parameters', example={
        'spot_price': 100.0,
        'strike': 105.0,
        'premium': 5.0
    })
})


@ns.route('/analyze')
class PnLAnalyze(Resource):
    """Analyze P&L for custom strategy."""

    @ns.doc('analyze_strategy')
    @ns.expect(analyze_request_model)
    def post(self):
        """Analyze P&L for a multi-leg custom strategy."""
        try:
            # Validate request
            data = AnalyzeRequest(**request.json)

            # Analyze strategy
            result = PnLService.analyze_strategy(
                strategy=data.strategy.dict(),
                market_params=data.market_params.dict()
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


@ns.route('/strategy-builder')
class PnLStrategyBuilder(Resource):
    """Build pre-defined strategy."""

    @ns.doc('build_strategy')
    @ns.expect(strategy_builder_model)
    def post(self):
        """Build and analyze a pre-defined strategy."""
        try:
            # Validate request
            data = StrategyBuilderRequest(**request.json)

            # Build strategy
            result = PnLService.build_strategy(
                strategy_name=data.strategy_name,
                parameters=data.parameters
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


@ns.route('/strategies')
class PnLStrategies(Resource):
    """Get available strategies."""

    @ns.doc('get_strategies')
    def get(self):
        """Get list of available pre-built strategies."""
        try:
            result = PnLService.get_available_strategies()
            return {
                'success': True,
                'data': result
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 500
