"""
Pydantic models for user authentication and profile management.
"""
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional
from datetime import datetime
import re


class UserRegister(BaseModel):
    """Request model for user registration."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    name: str = Field(..., min_length=2, max_length=100, description="User's display name")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('Invalid email format')
        return v.lower().strip()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        return v.strip()


class UserLogin(BaseModel):
    """Request model for user login."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return v.lower().strip()


class UserUpdate(BaseModel):
    """Request model for updating user profile."""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="User's display name")
    current_password: Optional[str] = Field(None, description="Current password (required for password change)")
    new_password: Optional[str] = Field(None, min_length=8, description="New password")

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if v is not None:
            if len(v) < 8:
                raise ValueError('Password must be at least 8 characters')
            if not re.search(r'[A-Za-z]', v):
                raise ValueError('Password must contain at least one letter')
            if not re.search(r'\d', v):
                raise ValueError('Password must contain at least one number')
        return v


class UserPreferences(BaseModel):
    """User preferences model."""
    theme: str = Field(default='light', description="UI theme preference")
    default_contract: Optional[str] = Field(None, description="Default contract symbol")
    notifications_enabled: bool = Field(default=True, description="Enable notifications")

    @field_validator('theme')
    @classmethod
    def validate_theme(cls, v):
        if v not in ['light', 'dark']:
            raise ValueError('Theme must be "light" or "dark"')
        return v


class UserPreferencesUpdate(BaseModel):
    """Request model for updating user preferences."""
    theme: Optional[str] = Field(None, description="UI theme preference")
    default_contract: Optional[str] = Field(None, description="Default contract symbol")
    notifications_enabled: Optional[bool] = Field(None, description="Enable notifications")

    @field_validator('theme')
    @classmethod
    def validate_theme(cls, v):
        if v is not None and v not in ['light', 'dark']:
            raise ValueError('Theme must be "light" or "dark"')
        return v


class UserProfile(BaseModel):
    """User profile response model."""
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    name: str = Field(..., description="User's display name")
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    created_at: datetime = Field(..., description="Account creation date")
    updated_at: Optional[datetime] = Field(None, description="Last update date")


class TokenResponse(BaseModel):
    """JWT token response model."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default='Bearer', description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
