"""
Authentication API endpoints.
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, get_jwt,
    create_access_token
)
from backend.services.auth_service import AuthService
from backend.models.user_models import (
    UserRegister, UserLogin, UserUpdate, UserPreferencesUpdate
)
from pydantic import ValidationError

# Create namespace
ns = Namespace('auth', description='Authentication and user management')

# API Models for Swagger documentation
register_model = ns.model('RegisterRequest', {
    'email': fields.String(required=True, description='User email', example='user@example.com'),
    'password': fields.String(required=True, description='Password (min 8 chars, must include letter and number)', example='Password123'),
    'name': fields.String(required=True, description='Display name', example='John Doe')
})

login_model = ns.model('LoginRequest', {
    'email': fields.String(required=True, description='User email', example='user@example.com'),
    'password': fields.String(required=True, description='Password', example='Password123')
})

update_profile_model = ns.model('UpdateProfileRequest', {
    'name': fields.String(description='Display name', example='John Doe'),
    'current_password': fields.String(description='Current password (required for password change)'),
    'new_password': fields.String(description='New password')
})

preferences_model = ns.model('PreferencesRequest', {
    'theme': fields.String(description='UI theme', example='dark', enum=['light', 'dark']),
    'default_contract': fields.String(description='Default contract symbol', example='SCOM'),
    'notifications_enabled': fields.Boolean(description='Enable notifications', example=True)
})

token_response = ns.model('TokenResponse', {
    'access_token': fields.String(description='JWT access token'),
    'refresh_token': fields.String(description='JWT refresh token'),
    'token_type': fields.String(description='Token type'),
    'expires_in': fields.Integer(description='Token expiration in seconds')
})

user_response = ns.model('UserResponse', {
    'id': fields.String(description='User ID'),
    'email': fields.String(description='User email'),
    'name': fields.String(description='Display name'),
    'preferences': fields.Raw(description='User preferences'),
    'created_at': fields.String(description='Account creation date'),
    'updated_at': fields.String(description='Last update date')
})


@ns.route('/register')
class Register(Resource):
    """User registration endpoint."""

    @ns.doc('register_user')
    @ns.expect(register_model)
    def post(self):
        """Register a new user account."""
        try:
            # Validate request
            data = UserRegister(**request.json)

            # Create user
            user = AuthService.create_user(
                email=data.email,
                password=data.password,
                name=data.name
            )

            # Generate tokens
            tokens = AuthService.generate_tokens(user['id'])

            return {
                'success': True,
                'message': 'Registration successful',
                'data': {
                    'user': user,
                    'tokens': tokens
                }
            }, 201

        except ValidationError as e:
            return {
                'success': False,
                'message': 'Validation error',
                'errors': e.errors()
            }, 400
        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }, 409
        except Exception as e:
            return {
                'success': False,
                'message': f'Registration failed: {str(e)}'
            }, 500


@ns.route('/login')
class Login(Resource):
    """User login endpoint."""

    @ns.doc('login_user')
    @ns.expect(login_model)
    def post(self):
        """Authenticate user and return tokens."""
        try:
            # Validate request
            data = UserLogin(**request.json)

            # Authenticate user
            user = AuthService.authenticate(
                email=data.email,
                password=data.password
            )

            if not user:
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }, 401

            # Generate tokens
            tokens = AuthService.generate_tokens(user['id'])

            return {
                'success': True,
                'message': 'Login successful',
                'data': {
                    'user': user,
                    'tokens': tokens
                }
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
                'message': f'Login failed: {str(e)}'
            }, 500


@ns.route('/refresh')
class RefreshToken(Resource):
    """Token refresh endpoint."""

    @ns.doc('refresh_token')
    @jwt_required(refresh=True)
    def post(self):
        """Refresh access token using refresh token."""
        try:
            user_id = get_jwt_identity()
            
            # Verify user still exists
            user = AuthService.get_user_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }, 404

            # Generate new access token
            access_token = create_access_token(identity=user_id)

            return {
                'success': True,
                'data': {
                    'access_token': access_token,
                    'token_type': 'Bearer'
                }
            }, 200

        except Exception as e:
            return {
                'success': False,
                'message': f'Token refresh failed: {str(e)}'
            }, 500


@ns.route('/profile')
class Profile(Resource):
    """User profile endpoint."""

    @ns.doc('get_profile')
    @jwt_required()
    def get(self):
        """Get current user's profile."""
        try:
            user_id = get_jwt_identity()
            user = AuthService.get_user_by_id(user_id)

            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }, 404

            return {
                'success': True,
                'data': user
            }, 200

        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get profile: {str(e)}'
            }, 500

    @ns.doc('update_profile')
    @ns.expect(update_profile_model)
    @jwt_required()
    def put(self):
        """Update current user's profile."""
        try:
            user_id = get_jwt_identity()
            data = UserUpdate(**request.json)

            # If changing password, verify current password
            if data.new_password:
                if not data.current_password:
                    return {
                        'success': False,
                        'message': 'Current password required to change password'
                    }, 400

                user = AuthService.get_user_by_id(user_id)
                if not user:
                    return {
                        'success': False,
                        'message': 'User not found'
                    }, 404

                # Verify current password by re-authenticating
                auth_check = AuthService.authenticate(user['email'], data.current_password)
                if not auth_check:
                    return {
                        'success': False,
                        'message': 'Current password is incorrect'
                    }, 401

            # Update user
            updates = data.model_dump(exclude_none=True)
            updated_user = AuthService.update_user(user_id, updates)

            if not updated_user:
                return {
                    'success': False,
                    'message': 'Failed to update profile'
                }, 500

            return {
                'success': True,
                'message': 'Profile updated successfully',
                'data': updated_user
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
                'message': f'Failed to update profile: {str(e)}'
            }, 500

    @ns.doc('delete_profile')
    @jwt_required()
    def delete(self):
        """Delete current user's account."""
        try:
            user_id = get_jwt_identity()

            if AuthService.delete_user(user_id):
                return {
                    'success': True,
                    'message': 'Account deleted successfully'
                }, 200

            return {
                'success': False,
                'message': 'Failed to delete account'
            }, 500

        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to delete account: {str(e)}'
            }, 500


@ns.route('/preferences')
class Preferences(Resource):
    """User preferences endpoint."""

    @ns.doc('get_preferences')
    @jwt_required()
    def get(self):
        """Get current user's preferences."""
        try:
            user_id = get_jwt_identity()
            user = AuthService.get_user_by_id(user_id)

            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }, 404

            return {
                'success': True,
                'data': user.get('preferences', {})
            }, 200

        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get preferences: {str(e)}'
            }, 500

    @ns.doc('update_preferences')
    @ns.expect(preferences_model)
    @jwt_required()
    def put(self):
        """Update current user's preferences."""
        try:
            user_id = get_jwt_identity()
            data = UserPreferencesUpdate(**request.json)

            # Update preferences
            preferences = data.model_dump(exclude_none=True)
            updated_user = AuthService.update_preferences(user_id, preferences)

            if not updated_user:
                return {
                    'success': False,
                    'message': 'Failed to update preferences'
                }, 500

            return {
                'success': True,
                'message': 'Preferences updated successfully',
                'data': updated_user.get('preferences', {})
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
                'message': f'Failed to update preferences: {str(e)}'
            }, 500


@ns.route('/verify')
class VerifyToken(Resource):
    """Token verification endpoint."""

    @ns.doc('verify_token')
    @jwt_required()
    def get(self):
        """Verify if current token is valid."""
        try:
            user_id = get_jwt_identity()
            user = AuthService.get_user_by_id(user_id)

            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }, 404

            return {
                'success': True,
                'data': {
                    'valid': True,
                    'user': user
                }
            }, 200

        except Exception as e:
            return {
                'success': False,
                'message': 'Invalid token'
            }, 401
