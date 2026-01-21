"""
Report generation service for creating PDF reports.
"""
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from bson import ObjectId


class ReportService:
    """Service class for generating PDF reports."""
    
    _mongo = None
    _initialized = False
    
    # Report storage directory (absolute path)
    REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")

    @classmethod
    def init_app(cls, mongo):
        """Initialize with MongoDB instance."""
        cls._mongo = mongo
        cls._initialized = False
        
        # Ensure reports directory exists
        os.makedirs(cls.REPORTS_DIR, exist_ok=True)

    @classmethod
    def _ensure_indexes(cls):
        """Ensure necessary indexes exist."""
        if cls._mongo is not None and not cls._initialized:
            try:
                cls._mongo.db.reports.create_index('user_id')
                cls._mongo.db.reports.create_index('created_at')
                cls._mongo.db.reports.create_index([('user_id', 1), ('report_type', 1)])
                cls._initialized = True
            except Exception as e:
                print(f"Warning: Could not create report indexes: {e}")

    @classmethod
    def _get_reports_collection(cls):
        """Get reports collection."""
        if cls._mongo is None:
            raise RuntimeError("ReportService not initialized. Call init_app first.")
        cls._ensure_indexes()
        return cls._mongo.db.reports

    @classmethod
    def _get_transactions_collection(cls):
        """Get transactions collection."""
        if cls._mongo is None:
            raise RuntimeError("ReportService not initialized.")
        return cls._mongo.db.wallet_transactions

    @classmethod
    def _get_sessions_collection(cls):
        """Get chat sessions collection."""
        if cls._mongo is None:
            raise RuntimeError("ReportService not initialized.")
        return cls._mongo.db.chat_sessions

    @classmethod
    def _get_users_collection(cls):
        """Get users collection."""
        if cls._mongo is None:
            raise RuntimeError("ReportService not initialized.")
        return cls._mongo.db.users

    @classmethod
    def generate_report(
        cls,
        user_id: str,
        report_type: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_charts: bool = True,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a PDF report.
        
        Args:
            user_id: User ID
            report_type: Type of report (transaction, chat, combined, activity)
            start_date: Start date for report data (defaults to 30 days ago)
            end_date: End date for report data (defaults to now)
            include_charts: Whether to include charts
            title: Custom report title
        
        Returns:
            dict: Report information including ID and file path
        """
        # Set default date range
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get user info
        users = cls._get_users_collection()
        user = users.find_one({'_id': ObjectId(user_id)})
        if not user:
            raise ValueError("User not found")
        
        # Generate report based on type
        if report_type == 'transaction':
            pdf_path, metadata = cls._generate_transaction_report(
                user_id, user, start_date, end_date, include_charts, title
            )
        elif report_type == 'chat':
            pdf_path, metadata = cls._generate_chat_report(
                user_id, user, start_date, end_date, title
            )
        elif report_type == 'combined':
            pdf_path, metadata = cls._generate_combined_report(
                user_id, user, start_date, end_date, include_charts, title
            )
        elif report_type == 'activity':
            pdf_path, metadata = cls._generate_activity_report(
                user_id, user, start_date, end_date, title
            )
        else:
            raise ValueError(f"Unknown report type: {report_type}")
        
        # Get file size
        file_size = os.path.getsize(pdf_path)
        
        # Save report record to database
        report_id = f"rep_{uuid.uuid4().hex}"
        report_data = {
            '_id': report_id,
            'user_id': user_id,
            'report_type': report_type,
            'title': title or metadata.get('title', f"{report_type.title()} Report"),
            'file_path': pdf_path,
            'file_size': file_size,
            'start_date': start_date,
            'end_date': end_date,
            'metadata': metadata,
            'created_at': datetime.utcnow()
        }
        
        reports = cls._get_reports_collection()
        reports.insert_one(report_data)
        
        return {
            'id': report_id,
            'user_id': user_id,
            'report_type': report_type,
            'title': report_data['title'],
            'file_path': pdf_path,
            'file_size': file_size,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'metadata': metadata,
            'created_at': report_data['created_at'].isoformat()
        }

    @classmethod
    def _generate_transaction_report(
        cls,
        user_id: str,
        user: Dict,
        start_date: datetime,
        end_date: datetime,
        include_charts: bool,
        title: Optional[str]
    ) -> tuple:
        """Generate transaction report PDF."""
        # Get transactions
        transactions = cls._get_transactions_collection()
        trans_cursor = transactions.find({
            'user_id': user_id,
            'created_at': {'$gte': start_date, '$lte': end_date}
        }).sort('created_at', -1)
        
        trans_list = list(trans_cursor)
        
        # Calculate metadata
        total_deposits = sum(t['amount'] for t in trans_list if t['type'] == 'deposit' and t['status'] == 'completed')
        total_payments = sum(t['amount'] for t in trans_list if t['type'] == 'payment' and t['status'] == 'completed')
        
        metadata = {
            'title': title or f"Transaction Report - {start_date.strftime('%b %Y')}",
            'transaction_count': len(trans_list),
            'total_deposits': total_deposits,
            'total_payments': total_payments,
            'net_amount': total_deposits - total_payments
        }
        
        # Create PDF
        filename = f"transaction_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(cls.REPORTS_DIR, user_id, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1A4D2E'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        story.append(Paragraph(metadata['title'], title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # User info
        user_info = f"""
        <b>User:</b> {user.get('name', 'N/A')}<br/>
        <b>Email:</b> {user.get('email', 'N/A')}<br/>
        <b>Report Period:</b> {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}<br/>
        <b>Generated:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
        """
        story.append(Paragraph(user_info, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary section
        story.append(Paragraph("<b>Summary</b>", styles['Heading2']))
        summary_data = [
            ['Metric', 'Value'],
            ['Total Transactions', str(metadata['transaction_count'])],
            ['Total Deposits', f"KES {metadata['total_deposits']:.2f}"],
            ['Total Payments', f"KES {metadata['total_payments']:.2f}"],
            ['Net Amount', f"KES {metadata['net_amount']:.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A4D2E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Transactions table
        if trans_list:
            story.append(Paragraph("<b>Transaction History</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            trans_data = [['Date', 'Type', 'Amount', 'Status', 'Description']]
            for trans in trans_list:
                trans_data.append([
                    trans['created_at'].strftime('%Y-%m-%d %H:%M') if trans.get('created_at') else 'N/A',
                    trans.get('type', 'N/A').title(),
                    f"KES {trans.get('amount', 0):.2f}",
                    trans.get('status', 'N/A').title(),
                    (trans.get('description', 'N/A')[:30] + '...') if len(trans.get('description', '')) > 30 else trans.get('description', 'N/A')
                ])
            
            trans_table = Table(trans_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 2*inch])
            trans_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A4D2E')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            story.append(trans_table)
        else:
            story.append(Paragraph("<i>No transactions found for this period.</i>", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return filepath, metadata

    @classmethod
    def _generate_chat_report(
        cls,
        user_id: str,
        user: Dict,
        start_date: datetime,
        end_date: datetime,
        title: Optional[str]
    ) -> tuple:
        """Generate chat sessions report PDF."""
        # Get chat sessions
        sessions = cls._get_sessions_collection()
        session_cursor = sessions.find({
            'user_id': user_id,
            'created_at': {'$gte': start_date, '$lte': end_date}
        }).sort('created_at', -1)
        
        session_list = list(session_cursor)
        
        # Calculate metadata
        total_messages = sum(len(s.get('messages', [])) for s in session_list)
        total_tokens = sum(s.get('total_tokens', 0) for s in session_list)
        
        metadata = {
            'title': title or f"AI Chat Report - {start_date.strftime('%b %Y')}",
            'session_count': len(session_list),
            'total_messages': total_messages,
            'total_tokens': total_tokens
        }
        
        # Create PDF
        filename = f"chat_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(cls.REPORTS_DIR, user_id, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1A4D2E'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        story.append(Paragraph(metadata['title'], title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # User info
        user_info = f"""
        <b>User:</b> {user.get('name', 'N/A')}<br/>
        <b>Email:</b> {user.get('email', 'N/A')}<br/>
        <b>Report Period:</b> {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}<br/>
        <b>Generated:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
        """
        story.append(Paragraph(user_info, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        story.append(Paragraph("<b>Summary</b>", styles['Heading2']))
        summary_data = [
            ['Metric', 'Value'],
            ['Chat Sessions', str(metadata['session_count'])],
            ['Total Messages', str(metadata['total_messages'])],
            ['Total Tokens Used', str(metadata['total_tokens'])]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A4D2E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Chat sessions
        if session_list:
            story.append(Paragraph("<b>Chat Sessions</b>", styles['Heading2']))
            
            for idx, session in enumerate(session_list[:10], 1):  # Limit to first 10 sessions
                story.append(Spacer(1, 0.2*inch))
                session_title = session.get('title', f"Session {idx}")
                story.append(Paragraph(f"<b>{idx}. {session_title}</b>", styles['Heading3']))
                
                session_info = f"""
                <b>Date:</b> {session['created_at'].strftime('%Y-%m-%d %H:%M') if session.get('created_at') else 'N/A'}<br/>
                <b>Messages:</b> {len(session.get('messages', []))}<br/>
                <b>Tokens:</b> {session.get('total_tokens', 0)}
                """
                story.append(Paragraph(session_info, styles['Normal']))
                
                # Show first few messages
                messages = session.get('messages', [])[:6]  # First 3 exchanges
                if messages:
                    story.append(Spacer(1, 0.1*inch))
                    for msg in messages:
                        role = msg.get('role', 'unknown')
                        content = msg.get('content', '')
                        if len(content) > 200:
                            content = content[:200] + '...'
                        
                        role_color = '#1A4D2E' if role == 'user' else '#2E8B57'
                        msg_style = ParagraphStyle(
                            f'Message_{role}',
                            parent=styles['Normal'],
                            fontSize=9,
                            leftIndent=10,
                            textColor=colors.HexColor(role_color)
                        )
                        story.append(Paragraph(f"<b>{role.title()}:</b> {content}", msg_style))
                        story.append(Spacer(1, 0.05*inch))
            
            if len(session_list) > 10:
                story.append(Paragraph(f"<i>... and {len(session_list) - 10} more sessions</i>", styles['Normal']))
        else:
            story.append(Paragraph("<i>No chat sessions found for this period.</i>", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return filepath, metadata

    @classmethod
    def _generate_combined_report(cls, user_id: str, user: Dict, start_date: datetime, end_date: datetime, include_charts: bool, title: Optional[str]) -> tuple:
        """Generate combined transaction and chat report."""
        # This would combine both transaction and chat data
        # For now, we'll create separate sections
        filename = f"combined_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(cls.REPORTS_DIR, user_id, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Simplified implementation - can be enhanced
        metadata = {'title': title or f"Combined Report - {start_date.strftime('%b %Y')}"}
        
        # For now, just create a placeholder PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        story.append(Paragraph(metadata['title'], styles['Title']))
        story.append(Paragraph("Combined report functionality - In development", styles['Normal']))
        doc.build(story)
        
        return filepath, metadata

    @classmethod
    def _generate_activity_report(cls, user_id: str, user: Dict, start_date: datetime, end_date: datetime, title: Optional[str]) -> tuple:
        """Generate user activity summary report."""
        filename = f"activity_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(cls.REPORTS_DIR, user_id, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        metadata = {'title': title or f"Activity Report - {start_date.strftime('%b %Y')}"}
        
        # Placeholder implementation
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        story.append(Paragraph(metadata['title'], styles['Title']))
        story.append(Paragraph("Activity report functionality - In development", styles['Normal']))
        doc.build(story)
        
        return filepath, metadata

    @classmethod
    def get_user_reports(cls, user_id: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get user's generated reports."""
        reports = cls._get_reports_collection()
        
        # Get total count
        total = reports.count_documents({'user_id': user_id})
        
        # Get paginated results
        skip = (page - 1) * per_page
        cursor = reports.find({'user_id': user_id}).sort('created_at', -1).skip(skip).limit(per_page)
        
        report_list = []
        for report in cursor:
            report_list.append({
                'id': report['_id'],
                'user_id': report['user_id'],
                'report_type': report['report_type'],
                'title': report['title'],
                'file_path': report['file_path'],
                'file_size': report['file_size'],
                'start_date': report['start_date'].isoformat() if report.get('start_date') else None,
                'end_date': report['end_date'].isoformat() if report.get('end_date') else None,
                'metadata': report.get('metadata', {}),
                'created_at': report['created_at'].isoformat() if report.get('created_at') else None
            })
        
        return {
            'reports': report_list,
            'total': total,
            'page': page,
            'per_page': per_page
        }

    @classmethod
    def get_report(cls, report_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific report."""
        reports = cls._get_reports_collection()
        
        report = reports.find_one({
            '_id': report_id,
            'user_id': user_id
        })
        
        if not report:
            return None
        
        return {
            'id': report['_id'],
            'user_id': report['user_id'],
            'report_type': report['report_type'],
            'title': report['title'],
            'file_path': report['file_path'],
            'file_size': report['file_size'],
            'start_date': report['start_date'].isoformat() if report.get('start_date') else None,
            'end_date': report['end_date'].isoformat() if report.get('end_date') else None,
            'metadata': report.get('metadata', {}),
            'created_at': report['created_at'].isoformat() if report.get('created_at') else None
        }

    @classmethod
    def delete_report(cls, report_id: str, user_id: str) -> bool:
        """Delete a report."""
        reports = cls._get_reports_collection()
        
        report = reports.find_one({
            '_id': report_id,
            'user_id': user_id
        })
        
        if not report:
            return False
        
        # Delete file if exists
        if os.path.exists(report['file_path']):
            os.remove(report['file_path'])
        
        # Delete database record
        reports.delete_one({'_id': report_id})
        
        return True
