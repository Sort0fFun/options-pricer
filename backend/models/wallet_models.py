"""
Pydantic models for wallet and M-Pesa payment management.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, List
from datetime import datetime
import re


class WalletBalance(BaseModel):
    """Wallet balance response model."""
    balance: float = Field(..., ge=0, description="Current wallet balance in KES")
    currency: str = Field(default='KES', description="Currency code")
    last_updated: Optional[datetime] = Field(None, description="Last balance update time")


class MpesaSTKRequest(BaseModel):
    """Request model for M-Pesa STK Push."""
    phone_number: str = Field(..., description="Phone number in format 2547XXXXXXXX or 07XXXXXXXX")
    amount: float = Field(..., gt=0, le=150000, description="Amount in KES (1-150,000)")
    description: Optional[str] = Field(default="Wallet top-up", max_length=100)

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        # Remove any spaces or special characters
        v = re.sub(r'[\s\-\+]', '', v)
        
        # Convert formats to 2547XXXXXXXX
        if v.startswith('07') or v.startswith('01'):
            v = '254' + v[1:]
        elif v.startswith('+254'):
            v = v[1:]
        elif v.startswith('7'):
            v = '254' + v
        
        # Validate format
        if not re.match(r'^254[17]\d{8}$', v):
            raise ValueError('Invalid phone number format. Use: 07XXXXXXXX or 2547XXXXXXXX')
        
        return v

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v < 1:
            raise ValueError('Minimum deposit amount is KES 1')
        if v > 150000:
            raise ValueError('Maximum deposit amount is KES 150,000')
        return round(v, 2)


class MpesaCallbackMetadataItem(BaseModel):
    """M-Pesa callback metadata item."""
    Name: str
    Value: Optional[str] = None


class MpesaCallbackMetadata(BaseModel):
    """M-Pesa callback metadata."""
    Item: List[MpesaCallbackMetadataItem] = []


class MpesaStkCallbackBody(BaseModel):
    """M-Pesa STK callback body."""
    MerchantRequestID: str
    CheckoutRequestID: str
    ResultCode: int
    ResultDesc: str
    CallbackMetadata: Optional[MpesaCallbackMetadata] = None


class MpesaStkCallback(BaseModel):
    """M-Pesa STK callback wrapper."""
    stkCallback: MpesaStkCallbackBody


class MpesaCallback(BaseModel):
    """M-Pesa callback request model."""
    Body: MpesaStkCallback


class WalletTransaction(BaseModel):
    """Wallet transaction model."""
    id: str = Field(..., description="Transaction ID")
    user_id: str = Field(..., description="User ID")
    type: Literal['deposit', 'withdrawal', 'payment', 'refund'] = Field(..., description="Transaction type")
    amount: float = Field(..., description="Transaction amount in KES")
    status: Literal['pending', 'completed', 'failed', 'cancelled'] = Field(..., description="Transaction status")
    description: Optional[str] = Field(None, description="Transaction description")
    mpesa_receipt: Optional[str] = Field(None, description="M-Pesa receipt number")
    mpesa_checkout_id: Optional[str] = Field(None, description="M-Pesa checkout request ID")
    phone_number: Optional[str] = Field(None, description="Phone number used")
    created_at: datetime = Field(..., description="Transaction creation time")
    updated_at: Optional[datetime] = Field(None, description="Last update time")


class TransactionListResponse(BaseModel):
    """Transaction list response model."""
    transactions: List[WalletTransaction]
    total: int
    page: int
    per_page: int


class PaymentRequest(BaseModel):
    """Request model for making a payment from wallet."""
    amount: float = Field(..., gt=0, description="Amount to pay in KES")
    description: str = Field(..., max_length=200, description="Payment description")
    service: Literal['chat', 'premium', 'other'] = Field(default='chat', description="Service being paid for")


class ChatTokenPurchase(BaseModel):
    """Request model for purchasing chat tokens."""
    tokens: int = Field(..., gt=0, le=100000, description="Number of tokens to purchase")
    custom: bool = Field(default=False, description="Whether this is a custom amount")
    
    @field_validator('tokens')
    @classmethod
    def validate_tokens(cls, v):
        if v < 10:
            raise ValueError('Minimum purchase is 10 tokens')
        if v > 100000:
            raise ValueError('Maximum purchase is 100,000 tokens')
        return v


class ChatTokenBalance(BaseModel):
    """Chat token balance model."""
    tokens: int = Field(default=0, ge=0, description="Available chat tokens")
    tokens_used: int = Field(default=0, ge=0, description="Total tokens used")
    last_purchase: Optional[datetime] = Field(None, description="Last token purchase date")


# Token pricing (KES per package)
TOKEN_PRICING = {
    100: 50,      # KES 50 for 100 tokens (KES 0.50/token)
    500: 200,     # KES 200 for 500 tokens (KES 0.40/token)
    1000: 350,    # KES 350 for 1000 tokens (KES 0.35/token)
    5000: 1500,   # KES 1500 for 5000 tokens (KES 0.30/token)
    10000: 2500,  # KES 2500 for 10000 tokens (KES 0.25/token)
}

# Base rate for custom amounts (KES per token)
BASE_TOKEN_RATE = 0.50

def calculate_custom_token_price(tokens: int) -> float:
    """Calculate price for custom token amounts with volume discounts."""
    if tokens < 10:
        raise ValueError('Minimum purchase is 10 tokens')
    
    # Volume discount tiers
    if tokens >= 10000:
        rate = 0.25  # 50% discount
    elif tokens >= 5000:
        rate = 0.30  # 40% discount
    elif tokens >= 1000:
        rate = 0.35  # 30% discount
    elif tokens >= 500:
        rate = 0.40  # 20% discount
    elif tokens >= 100:
        rate = 0.50  # base rate
    else:
        rate = 0.50  # base rate for small amounts
    
    return round(tokens * rate, 2)
