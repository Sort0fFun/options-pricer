"""
Wallet API endpoints for balance, deposits, and chat tokens.
"""
from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError

from backend.models.wallet_models import (
    MpesaSTKRequest,
    ChatTokenPurchase,
    TOKEN_PRICING,
    calculate_custom_token_price
)
from backend.services.wallet_service import WalletService
from backend.services.mpesa_service import MpesaService


# Create namespace
wallet_ns = Namespace('wallet', description='Wallet and payment operations')

# API models for documentation
wallet_model = wallet_ns.model('Wallet', {
    'balance': fields.Float(description='Wallet balance in KES'),
    'currency': fields.String(description='Currency code'),
    'chat_tokens': fields.Integer(description='Available chat tokens'),
    'tokens_used': fields.Integer(description='Total tokens used'),
    'last_updated': fields.String(description='Last update timestamp')
})

stk_request_model = wallet_ns.model('STKPushRequest', {
    'phone_number': fields.String(required=True, description='M-Pesa phone number (254...)'),
    'amount': fields.Float(required=True, description='Amount in KES (min 10)')
})

stk_response_model = wallet_ns.model('STKPushResponse', {
    'checkout_request_id': fields.String(description='M-Pesa checkout request ID'),
    'merchant_request_id': fields.String(description='Merchant request ID'),
    'response_description': fields.String(description='Response message'),
    'transaction_id': fields.String(description='Internal transaction ID')
})

token_purchase_model = wallet_ns.model('TokenPurchase', {
    'tokens': fields.Integer(required=True, description='Number of tokens to purchase')
})

transaction_model = wallet_ns.model('Transaction', {
    'id': fields.String(description='Transaction ID'),
    'type': fields.String(description='Transaction type'),
    'amount': fields.Float(description='Amount'),
    'status': fields.String(description='Transaction status'),
    'description': fields.String(description='Transaction description'),
    'mpesa_receipt': fields.String(description='M-Pesa receipt number'),
    'created_at': fields.String(description='Creation timestamp')
})


@wallet_ns.route('/balance')
class WalletBalance(Resource):
    """Get wallet balance."""
    
    @jwt_required()
    @wallet_ns.marshal_with(wallet_model)
    def get(self):
        """Get current wallet balance and token count."""
        user_id = get_jwt_identity()
        
        try:
            wallet = WalletService.get_wallet(user_id)
            return wallet, 200
        except ValueError as e:
            wallet_ns.abort(404, str(e))
        except Exception as e:
            current_app.logger.error(f"Error getting wallet: {e}")
            wallet_ns.abort(500, "Failed to get wallet balance")


@wallet_ns.route('/deposit')
class WalletDeposit(Resource):
    """Initiate M-Pesa deposit."""
    
    @jwt_required()
    @wallet_ns.expect(stk_request_model)
    @wallet_ns.marshal_with(stk_response_model)
    def post(self):
        """Initiate M-Pesa STK Push for wallet deposit."""
        user_id = get_jwt_identity()
        data = request.get_json()
        
        try:
            # Validate request
            stk_request = MpesaSTKRequest(**data)
        except ValidationError as e:
            wallet_ns.abort(400, str(e.errors()[0]['msg']))
        
        try:
            # Initiate STK push
            mpesa_response = MpesaService.initiate_stk_push(
                phone_number=stk_request.phone_number,
                amount=int(stk_request.amount),
                account_reference=f"Wallet-{user_id[:8]}",
                transaction_desc="Wallet Top-up"
            )
            
            if not mpesa_response.get('success'):
                wallet_ns.abort(400, mpesa_response.get('error', 'M-Pesa request failed'))
            
            # Create pending transaction
            transaction_id = WalletService.create_pending_deposit(
                user_id=user_id,
                amount=stk_request.amount,
                phone_number=stk_request.phone_number,
                checkout_request_id=mpesa_response['checkout_request_id'],
                merchant_request_id=mpesa_response['merchant_request_id']
            )
            
            return {
                'checkout_request_id': mpesa_response['checkout_request_id'],
                'merchant_request_id': mpesa_response['merchant_request_id'],
                'response_description': mpesa_response.get('response_description', 'STK push sent'),
                'transaction_id': transaction_id
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"M-Pesa STK push error: {e}")
            wallet_ns.abort(500, "Failed to initiate payment")


@wallet_ns.route('/deposit/status/<string:checkout_id>')
class DepositStatus(Resource):
    """Check deposit status."""
    
    @jwt_required()
    def get(self, checkout_id):
        """Check the status of a deposit transaction."""
        user_id = get_jwt_identity()
        
        try:
            # Get transaction from database
            transaction = WalletService.get_transaction_by_checkout_id(checkout_id)
            
            if not transaction:
                wallet_ns.abort(404, "Transaction not found")
            
            # Verify ownership
            if transaction['user_id'] != user_id:
                wallet_ns.abort(403, "Access denied")
            
            # If still pending, query M-Pesa for info but DON'T update status
            # The callback is the authoritative source for status updates
            mpesa_status = None
            if transaction['status'] == 'pending':
                try:
                    mpesa_status = MpesaService.query_stk_status(checkout_id)
                    # Only update if M-Pesa confirms success (ResultCode 0)
                    # Don't mark as failed here - let the callback handle failures
                    if mpesa_status.get('result_code') == 0:
                        WalletService.complete_deposit(
                            checkout_id,
                            mpesa_status.get('mpesa_receipt', ''),
                            transaction['amount']
                        )
                        transaction['status'] = 'completed'
                except Exception as e:
                    current_app.logger.warning(f"M-Pesa status query failed: {e}")
            
            return {
                'transaction': transaction,
                'wallet': WalletService.get_wallet(user_id),
                'mpesa_status': mpesa_status
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"Error checking deposit status: {e}")
            wallet_ns.abort(500, "Failed to check deposit status")


@wallet_ns.route('/callback')
class MpesaCallback(Resource):
    """M-Pesa callback endpoint."""
    
    def post(self):
        """Handle M-Pesa STK Push callback."""
        data = request.get_json()
        
        current_app.logger.info(f"M-Pesa callback received: {data}")
        
        try:
            # Parse callback
            callback_result = MpesaService.parse_callback(data)
            current_app.logger.info(f"Parsed callback: {callback_result}")
            
            if callback_result.get('success'):
                # Payment successful
                result = WalletService.complete_deposit(
                    callback_result['checkout_request_id'],
                    callback_result.get('mpesa_receipt', ''),
                    callback_result.get('amount', 0)
                )
                current_app.logger.info(f"Deposit completed: {result}")
            else:
                # Payment failed
                result = WalletService.fail_deposit(
                    callback_result.get('checkout_request_id', ''),
                    callback_result.get('result_desc', 'Payment failed')
                )
                current_app.logger.info(f"Deposit failed: {result}")
            
            # Always return success to M-Pesa
            return {"ResultCode": 0, "ResultDesc": "Accepted"}, 200
            
        except Exception as e:
            current_app.logger.error(f"M-Pesa callback error: {e}")
            return {"ResultCode": 0, "ResultDesc": "Accepted"}, 200


@wallet_ns.route('/tokens')
class ChatTokens(Resource):
    """Purchase chat tokens."""
    
    @jwt_required()
    def get(self):
        """Get available token packages and pricing info."""
        return {
            'packages': [
                {'tokens': tokens, 'price': price, 'label': f'{tokens} tokens'}
                for tokens, price in TOKEN_PRICING.items()
            ],
            'custom_pricing': {
                'min_tokens': 10,
                'max_tokens': 100000,
                'tiers': [
                    {'min': 10, 'max': 99, 'rate': 0.50, 'discount': '0%'},
                    {'min': 100, 'max': 499, 'rate': 0.50, 'discount': '0%'},
                    {'min': 500, 'max': 999, 'rate': 0.40, 'discount': '20%'},
                    {'min': 1000, 'max': 4999, 'rate': 0.35, 'discount': '30%'},
                    {'min': 5000, 'max': 9999, 'rate': 0.30, 'discount': '40%'},
                    {'min': 10000, 'max': 100000, 'rate': 0.25, 'discount': '50%'},
                ]
            },
            'description': 'Purchase tokens to use the AI chat assistant'
        }, 200
    
    @jwt_required()
    @wallet_ns.expect(token_purchase_model)
    def post(self):
        """Purchase chat tokens using wallet balance."""
        user_id = get_jwt_identity()
        data = request.get_json()
        
        try:
            # Validate request
            purchase = ChatTokenPurchase(**data)
        except ValidationError as e:
            wallet_ns.abort(400, str(e.errors()[0]['msg']))
        
        try:
            # Get price - use predefined package or calculate custom
            if purchase.custom or purchase.tokens not in TOKEN_PRICING:
                price = calculate_custom_token_price(purchase.tokens)
            else:
                price = TOKEN_PRICING.get(purchase.tokens)
            
            # Purchase tokens
            transaction = WalletService.purchase_tokens(user_id, purchase.tokens, price)
            wallet = WalletService.get_wallet(user_id)
            
            return {
                'message': f'Successfully purchased {purchase.tokens} tokens',
                'transaction': transaction,
                'wallet': wallet
            }, 200
            
        except ValueError as e:
            wallet_ns.abort(400, str(e))
        except Exception as e:
            current_app.logger.error(f"Token purchase error: {e}")
            wallet_ns.abort(500, "Failed to purchase tokens")


@wallet_ns.route('/tokens/use')
class UseToken(Resource):
    """Use chat tokens."""
    
    @jwt_required()
    def post(self):
        """Use a chat token (called when sending a message)."""
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        count = data.get('count', 1)
        
        try:
            success = WalletService.use_token(user_id, count)
            
            if not success:
                wallet_ns.abort(402, "Insufficient chat tokens. Please purchase more.")
            
            wallet = WalletService.get_wallet(user_id)
            return {
                'success': True,
                'tokens_remaining': wallet.get('chat_tokens', 0)
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"Token use error: {e}")
            wallet_ns.abort(500, "Failed to use token")


@wallet_ns.route('/transactions')
class Transactions(Resource):
    """Get transaction history."""
    
    @jwt_required()
    def get(self):
        """Get user's transaction history."""
        user_id = get_jwt_identity()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        transaction_type = request.args.get('type', None)
        
        try:
            result = WalletService.get_transactions(
                user_id, 
                page=page, 
                per_page=per_page,
                transaction_type=transaction_type
            )
            return result, 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting transactions: {e}")
            wallet_ns.abort(500, "Failed to get transactions")


@wallet_ns.route('/transactions/<string:transaction_id>')
class TransactionDetail(Resource):
    """Get transaction details."""
    
    @jwt_required()
    def get(self, transaction_id):
        """Get details of a specific transaction."""
        user_id = get_jwt_identity()
        
        try:
            transaction = WalletService.get_transaction_by_id(transaction_id)
            
            if not transaction:
                wallet_ns.abort(404, "Transaction not found")
            
            if transaction['user_id'] != user_id:
                wallet_ns.abort(403, "Access denied")
            
            return transaction, 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting transaction: {e}")
            wallet_ns.abort(500, "Failed to get transaction")
