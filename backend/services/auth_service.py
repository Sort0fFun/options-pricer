"""
Authentication service for user management with MongoDB.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token

bcrypt = Bcrypt()


class AuthService:
    """Service class for authentication operations."""

    _mongo = None
    _initialized = False

    @classmethod
    def init_app(cls, mongo):
        """Initialize with MongoDB instance."""
        cls._mongo = mongo
        # Index creation is deferred until first actual use
        # This prevents blocking app startup when MongoDB is not available
        cls._initialized = False

    @classmethod
    def _ensure_indexes(cls):
        """Ensure necessary indexes exist."""
        if cls._mongo is not None:
            cls._mongo.db.users.create_index('email', unique=True)
            cls._initialized = True

    @classmethod
    def _get_users_collection(cls):
        """Get users collection."""
        if cls._mongo is None:
            raise RuntimeError("AuthService not initialized. Call init_app first.")
        
        # Try to ensure indexes on first actual use
        if not cls._initialized:
            try:
                cls._ensure_indexes()
            except Exception as e:
                raise RuntimeError(f"MongoDB connection failed: {e}")
        
        return cls._mongo.db.users

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash a password using bcrypt."""
        return bcrypt.generate_password_hash(password).decode('utf-8')

    @classmethod
    def verify_password(cls, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.check_password_hash(password_hash, password)

    @classmethod
    def create_user(cls, email: str, password: str, name: str) -> Dict[str, Any]:
        """
        Create a new user.
        
        Args:
            email: User's email address
            password: Plain text password
            name: User's display name
            
        Returns:
            Created user document (without password)
            
        Raises:
            ValueError: If email already exists
        """
        users = cls._get_users_collection()

        # Check if user exists
        if users.find_one({'email': email}):
            raise ValueError('Email already registered')

        # Create user document
        now = datetime.utcnow()
        user_doc = {
            'email': email,
            'password_hash': cls.hash_password(password),
            'name': name,
            'preferences': {
                'theme': 'light',
                'default_contract': None,
                'notifications_enabled': True
            },
            'created_at': now,
            'updated_at': now
        }

        # Insert user
        result = users.insert_one(user_doc)
        user_doc['_id'] = result.inserted_id

        # Return user without password hash
        return cls._format_user(user_doc)

    @classmethod
    def authenticate(cls, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user by email and password.
        
        Args:
            email: User's email address
            password: Plain text password
            
        Returns:
            User document if authentication successful, None otherwise
        """
        users = cls._get_users_collection()
        user = users.find_one({'email': email})

        if user and cls.verify_password(password, user['password_hash']):
            return cls._format_user(user)

        return None

    @classmethod
    def get_user_by_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        users = cls._get_users_collection()
        try:
            user = users.find_one({'_id': ObjectId(user_id)})
            return cls._format_user(user) if user else None
        except Exception:
            return None

    @classmethod
    def get_user_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        users = cls._get_users_collection()
        user = users.find_one({'email': email})
        return cls._format_user(user) if user else None

    @classmethod
    def update_user(cls, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update user profile.
        
        Args:
            user_id: User's ID
            updates: Dictionary of fields to update
            
        Returns:
            Updated user document
        """
        users = cls._get_users_collection()

        # Handle password update
        if 'new_password' in updates:
            updates['password_hash'] = cls.hash_password(updates.pop('new_password'))
        updates.pop('current_password', None)

        # Remove None values
        updates = {k: v for k, v in updates.items() if v is not None}

        if not updates:
            return cls.get_user_by_id(user_id)

        updates['updated_at'] = datetime.utcnow()

        try:
            result = users.find_one_and_update(
                {'_id': ObjectId(user_id)},
                {'$set': updates},
                return_document=True
            )
            return cls._format_user(result) if result else None
        except Exception:
            return None

    @classmethod
    def update_preferences(cls, user_id: str, preferences: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update user preferences.
        
        Args:
            user_id: User's ID
            preferences: Dictionary of preferences to update
            
        Returns:
            Updated user document
        """
        users = cls._get_users_collection()

        # Remove None values
        preferences = {k: v for k, v in preferences.items() if v is not None}

        if not preferences:
            return cls.get_user_by_id(user_id)

        # Build update dict with dot notation for nested fields
        update_dict = {f'preferences.{k}': v for k, v in preferences.items()}
        update_dict['updated_at'] = datetime.utcnow()

        try:
            result = users.find_one_and_update(
                {'_id': ObjectId(user_id)},
                {'$set': update_dict},
                return_document=True
            )
            return cls._format_user(result) if result else None
        except Exception:
            return None

    @classmethod
    def delete_user(cls, user_id: str) -> bool:
        """Delete a user account."""
        users = cls._get_users_collection()
        try:
            result = users.delete_one({'_id': ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    @classmethod
    def generate_tokens(cls, user_id: str) -> Dict[str, Any]:
        """
        Generate JWT access and refresh tokens.
        
        Args:
            user_id: User's ID
            
        Returns:
            Dictionary with access_token, refresh_token, and expiration info
        """
        from flask import current_app

        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)

        expires_in = int(current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': expires_in
        }

    @classmethod
    def _format_user(cls, user: Dict[str, Any]) -> Dict[str, Any]:
        """Format user document for API response (remove sensitive data)."""
        if not user:
            return None

        return {
            'id': str(user['_id']),
            'email': user['email'],
            'name': user['name'],
            'preferences': user.get('preferences', {
                'theme': 'light',
                'default_contract': None,
                'notifications_enabled': True
            }),
            'created_at': user['created_at'].isoformat() if user.get('created_at') else None,
            'updated_at': user['updated_at'].isoformat() if user.get('updated_at') else None
        }
