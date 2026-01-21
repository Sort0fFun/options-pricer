"""
Pydantic models for report generation and management.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, List, Union
from datetime import datetime


class ReportGenerationRequest(BaseModel):
    """Request model for generating a report."""
    report_type: Literal['transaction', 'chat', 'combined', 'activity'] = Field(
        ..., 
        description="Type of report to generate"
    )
    start_date: Optional[Union[datetime, str]] = Field(
        None, 
        description="Start date for report data (defaults to 30 days ago)"
    )
    end_date: Optional[Union[datetime, str]] = Field(
        None, 
        description="End date for report data (defaults to now)"
    )
    include_charts: bool = Field(
        default=True, 
        description="Whether to include charts in the report"
    )
    title: Optional[str] = Field(
        None, 
        description="Custom report title"
    )
    
    @field_validator('start_date', 'end_date', mode='before')
    @classmethod
    def parse_date(cls, v):
        """Parse date from string if needed."""
        if v is None or v == '':
            return None
        if isinstance(v, str):
            try:
                # Try ISO format first
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except:
                try:
                    # Try date-only format (from HTML date input)
                    return datetime.strptime(v, '%Y-%m-%d')
                except:
                    return None
        return v


class Report(BaseModel):
    """Report model."""
    id: str = Field(..., description="Report ID")
    user_id: str = Field(..., description="User ID who generated the report")
    report_type: Literal['transaction', 'chat', 'combined', 'activity'] = Field(
        ..., 
        description="Type of report"
    )
    title: str = Field(..., description="Report title")
    file_path: str = Field(..., description="Path to generated PDF file")
    file_size: int = Field(..., description="File size in bytes")
    start_date: datetime = Field(..., description="Report data start date")
    end_date: datetime = Field(..., description="Report data end date")
    metadata: dict = Field(
        default_factory=dict, 
        description="Additional metadata (transaction count, message count, etc.)"
    )
    created_at: datetime = Field(..., description="Report creation time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "rep_1234567890",
                "user_id": "user_123",
                "report_type": "transaction",
                "title": "Transaction Report - January 2026",
                "file_path": "reports/user_123/transaction_20260120_143025.pdf",
                "file_size": 245678,
                "start_date": "2026-01-01T00:00:00",
                "end_date": "2026-01-20T23:59:59",
                "metadata": {
                    "transaction_count": 15,
                    "total_deposits": 5000.00,
                    "total_payments": 350.00
                },
                "created_at": "2026-01-20T14:30:25"
            }
        }


class ReportResponse(BaseModel):
    """Response model for a single report."""
    report: Report
    download_url: Optional[str] = Field(None, description="URL to download the report")


class ReportListResponse(BaseModel):
    """Response model for list of reports."""
    reports: List[Report]
    total: int = Field(..., description="Total number of reports")
    page: int = Field(default=1, description="Current page number")
    per_page: int = Field(default=20, description="Reports per page")
