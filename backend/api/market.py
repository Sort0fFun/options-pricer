"""
Market API endpoints.
"""
from flask import request
from flask_restx import Namespace, Resource
from backend.services.market_service import MarketService

# Create namespace
ns = Namespace('market', description='Market data and status operations')


@ns.route('/status')
class MarketStatus(Resource):
    """Get NSE market status."""

    @ns.doc('get_market_status')
    def get(self):
        """Get current market status (OPEN/CLOSED) with countdown."""
        try:
            result = MarketService.get_market_status()
            return {
                'success': True,
                'data': result
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 500


@ns.route('/futures')
class MarketFutures(Resource):
    """Get NSE futures market data."""

    @ns.doc('get_futures_data')
    @ns.param('contracts', 'Comma-separated contract symbols', type='string')
    @ns.param('types', 'Comma-separated contract types', type='string')
    def get(self):
        """Get filtered NSE futures data from CSV."""
        try:
            # Parse query parameters
            contracts_param = request.args.get('contracts')
            types_param = request.args.get('types')

            contracts = contracts_param.split(',') if contracts_param else None
            types = types_param.split(',') if types_param else None

            result = MarketService.get_futures_data(
                contracts=contracts,
                types=types
            )

            return {
                'success': True,
                'data': result
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 500
