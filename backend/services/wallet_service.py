"""
Wallet service for user balance and transaction management.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId
import uuid


class WalletService:
    """Service class for wallet operations."""
    
    _mongo = None
    _initialized = False

    @classmethod
    def init_app(cls, mongo):
        """Initialize with MongoDB instance."""
        cls._mongo = mongo
        cls._initialized = False

    @classmethod
    def _ensure_indexes(cls):
        """Ensure necessary indexes exist."""
        if cls._mongo is not None and not cls._initialized:
            try:
                cls._mongo.db.wallet_transactions.create_index('user_id')
                cls._mongo.db.wallet_transactions.create_index('mpesa_checkout_id')
                cls._mongo.db.wallet_transactions.create_index('status')
                cls._mongo.db.wallet_transactions.create_index('created_at')
                cls._initialized = True
            except Exception as e:
                print(f"Warning: Could not create wallet indexes: {e}")

    @classmethod
    def _get_users_collection(cls):
        """Get users collection."""
        if cls._mongo is None:
            raise RuntimeError("WalletService not initialized. Call init_app first.")
        cls._ensure_indexes()
        return cls._mongo.db.users

    @classmethod
    def _get_transactions_collection(cls):
        """Get transactions collection."""
        if cls._mongo is None:
            raise RuntimeError("WalletService not initialized. Call init_app first.")
        cls._ensure_indexes()
        return cls._mongo.db.wallet_transactions

    @classmethod
    def get_wallet(cls, user_id: str) -> Dict[str, Any]:
        """Get user's wallet balance and info."""
        users = cls._get_users_collection()
        
        try:
            user = users.find_one({'_id': ObjectId(user_id)})
        except Exception:
            raise ValueError("Invalid user ID")
        
        if not user:
            raise ValueError("User not found")
        
        # Return wallet or create default
        wallet = user.get('wallet', {
            'balance': 0.0,
            'currency': 'KES',
            'chat_tokens': 0,
            'tokens_used': 0,
            'last_updated': None
        })
        
        # Serialize datetime fields for JSON response
        if wallet.get('last_updated') and hasattr(wallet['last_updated'], 'isoformat'):
            wallet['last_updated'] = wallet['last_updated'].isoformat()
        if wallet.get('last_token_purchase') and hasattr(wallet['last_token_purchase'], 'isoformat'):
            wallet['last_token_purchase'] = wallet['last_token_purchase'].isoformat()
        
        return wallet

    @classmethod
    def ensure_wallet_exists(cls, user_id: str) -> None:
        """Ensure user has a wallet initialized."""
        users = cls._get_users_collection()
        
        users.update_one(
            {'_id': ObjectId(user_id), 'wallet': {'$exists': False}},
            {
                '$set': {
                    'wallet': {
                        'balance': 0.0,
                        'currency': 'KES',
                        'chat_tokens': 0,
                        'tokens_used': 0,
                        'last_updated': datetime.utcnow()
                    }
                }
            }
        )

    @classmethod
    def create_pending_deposit(
        cls,
        user_id: str,
        amount: float,
        phone_number: str,
        checkout_request_id: str,
        merchant_request_id: str
    ) -> str:
        """Create a pending deposit transaction."""
        transactions = cls._get_transactions_collection()
        
        # Ensure wallet exists
        cls.ensure_wallet_exists(user_id)
        
        transaction_id = str(uuid.uuid4())
        
        transaction = {
            '_id': transaction_id,
            'user_id': user_id,
            'type': 'deposit',
            'amount': amount,
            'status': 'pending',
            'description': 'M-Pesa wallet top-up',
            'phone_number': phone_number,
            'mpesa_checkout_id': checkout_request_id,
            'mpesa_merchant_id': merchant_request_id,
            'mpesa_receipt': None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        transactions.insert_one(transaction)
        return transaction_id

    @classmethod
    def complete_deposit(
        cls,
        checkout_request_id: str,
        mpesa_receipt: str,
        amount: float
    ) -> Optional[Dict[str, Any]]:
        """Complete a pending deposit after successful M-Pesa callback."""
        transactions = cls._get_transactions_collection()
        users = cls._get_users_collection()
        
        # Find and update transaction
        transaction = transactions.find_one_and_update(
            {'mpesa_checkout_id': checkout_request_id, 'status': 'pending'},
            {
                '$set': {
                    'status': 'completed',
                    'mpesa_receipt': mpesa_receipt,
                    'updated_at': datetime.utcnow()
                }
            },
            return_document=True
        )
        
        if not transaction:
            return None
        
        # Credit user's wallet
        result = users.update_one(
            {'_id': ObjectId(transaction['user_id'])},
            {
                '$inc': {'wallet.balance': amount},
                '$set': {'wallet.last_updated': datetime.utcnow()}
            }
        )
        
        # If wallet didn't exist, create it with the amount
        if result.modified_count == 0:
            users.update_one(
                {'_id': ObjectId(transaction['user_id'])},
                {
                    '$set': {
                        'wallet': {
                            'balance': amount,
                            'currency': 'KES',
                            'chat_tokens': 0,
                            'tokens_used': 0,
                            'last_updated': datetime.utcnow()
                        }
                    }
                }
            )
        
        return cls._format_transaction(transaction)

    @classmethod
    def fail_deposit(cls, checkout_request_id: str, reason: str) -> Optional[Dict[str, Any]]:
        """Mark a deposit as failed."""
        transactions = cls._get_transactions_collection()
        
        transaction = transactions.find_one_and_update(
            {'mpesa_checkout_id': checkout_request_id, 'status': 'pending'},
            {
                '$set': {
                    'status': 'failed',
                    'description': f'M-Pesa payment failed: {reason}',
                    'updated_at': datetime.utcnow()
                }
            },
            return_document=True
        )
        
        return cls._format_transaction(transaction) if transaction else None

    @classmethod
    def debit_wallet(
        cls,
        user_id: str,
        amount: float,
        description: str,
        transaction_type: str = 'payment'
    ) -> Dict[str, Any]:
        """Debit amount from user's wallet."""
        users = cls._get_users_collection()
        transactions = cls._get_transactions_collection()
        
        # Check balance
        wallet = cls.get_wallet(user_id)
        if wallet.get('balance', 0) < amount:
            raise ValueError(f"Insufficient balance. Available: KES {wallet.get('balance', 0):.2f}")
        
        # Deduct from wallet
        users.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$inc': {'wallet.balance': -amount},
                '$set': {'wallet.last_updated': datetime.utcnow()}
            }
        )
        
        # Record transaction
        transaction_id = str(uuid.uuid4())
        transaction = {
            '_id': transaction_id,
            'user_id': user_id,
            'type': transaction_type,
            'amount': -amount,  # Negative for debits
            'status': 'completed',
            'description': description,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        transactions.insert_one(transaction)
        
        return cls._format_transaction(transaction)

    @classmethod
    def credit_wallet(
        cls,
        user_id: str,
        amount: float,
        description: str,
        transaction_type: str = 'refund'
    ) -> Dict[str, Any]:
        """Credit amount to user's wallet."""
        users = cls._get_users_collection()
        transactions = cls._get_transactions_collection()
        
        # Ensure wallet exists
        cls.ensure_wallet_exists(user_id)
        
        # Add to wallet
        users.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$inc': {'wallet.balance': amount},
                '$set': {'wallet.last_updated': datetime.utcnow()}
            }
        )
        
        # Record transaction
        transaction_id = str(uuid.uuid4())
        transaction = {
            '_id': transaction_id,
            'user_id': user_id,
            'type': transaction_type,
            'amount': amount,
            'status': 'completed',
            'description': description,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        transactions.insert_one(transaction)
        
        return cls._format_transaction(transaction)

    @classmethod
    def purchase_tokens(cls, user_id: str, tokens: int, price: float) -> Dict[str, Any]:
        """Purchase chat tokens using wallet balance."""
        users = cls._get_users_collection()
        
        # Debit wallet
        transaction = cls.debit_wallet(
            user_id, 
            price, 
            f'Purchased {tokens} chat tokens',
            'payment'
        )
        
        # Credit tokens
        users.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$inc': {'wallet.chat_tokens': tokens},
                '$set': {'wallet.last_token_purchase': datetime.utcnow()}
            }
        )
        
        return transaction

    @classmethod
    def use_token(cls, user_id: str, count: int = 1) -> bool:
        """Use chat tokens. Returns True if successful."""
        users = cls._get_users_collection()
        wallet = cls.get_wallet(user_id)
        
        if wallet.get('chat_tokens', 0) < count:
            return False
        
        users.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$inc': {
                    'wallet.chat_tokens': -count,
                    'wallet.tokens_used': count
                }
            }
        )
        
        return True

    @classmethod
    def get_transactions(
        cls,
        user_id: str,
        page: int = 1,
        per_page: int = 20,
        transaction_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user's transaction history."""
        transactions = cls._get_transactions_collection()
        
        query = {'user_id': user_id}
        if transaction_type:
            query['type'] = transaction_type
        
        total = transactions.count_documents(query)
        skip = (page - 1) * per_page
        
        cursor = transactions.find(query).sort('created_at', -1).skip(skip).limit(per_page)
        
        items = [cls._format_transaction(doc) for doc in cursor]
        
        return {
            'transactions': items,
            'total': total,
            'page': page,
            'per_page': per_page
        }

    @classmethod
    def get_transaction_by_checkout_id(cls, checkout_request_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction by M-Pesa checkout request ID."""
        transactions = cls._get_transactions_collection()
        doc = transactions.find_one({'mpesa_checkout_id': checkout_request_id})
        
        return cls._format_transaction(doc) if doc else None

    @classmethod
    def get_transaction_by_id(cls, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction by ID."""
        transactions = cls._get_transactions_collection()
        doc = transactions.find_one({'_id': transaction_id})
        
        return cls._format_transaction(doc) if doc else None

    @classmethod
    def _format_transaction(cls, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Format transaction document for API response."""
        if not doc:
            return None
        
        return {
            'id': doc['_id'],
            'user_id': doc['user_id'],
            'type': doc['type'],
            'amount': doc['amount'],
            'status': doc['status'],
            'description': doc.get('description'),
            'mpesa_receipt': doc.get('mpesa_receipt'),
            'mpesa_checkout_id': doc.get('mpesa_checkout_id'),
            'phone_number': doc.get('phone_number'),
            'created_at': doc['created_at'].isoformat() if doc.get('created_at') else None,
            'updated_at': doc['updated_at'].isoformat() if doc.get('updated_at') else None
        }
