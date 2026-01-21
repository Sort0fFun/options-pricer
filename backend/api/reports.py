"""
Reports API endpoints for generating and managing reports.
"""
from flask import request, send_file
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError
from datetime import datetime
import os

from backend.models.report import ReportGenerationRequest
from backend.services.report_service import ReportService


# Create namespace
reports_ns = Namespace('reports', description='Report generation and management')

# API models for documentation
report_generation_model = reports_ns.model('ReportGeneration', {
    'report_type': fields.String(
        required=True,
        description='Type of report',
        enum=['transaction', 'chat', 'combined', 'activity']
    ),
    'start_date': fields.DateTime(description='Start date (ISO format)'),
    'end_date': fields.DateTime(description='End date (ISO format)'),
    'include_charts': fields.Boolean(default=True, description='Include charts in report'),
    'title': fields.String(description='Custom report title')
})

report_model = reports_ns.model('Report', {
    'id': fields.String(description='Report ID'),
    'user_id': fields.String(description='User ID'),
    'report_type': fields.String(description='Report type'),
    'title': fields.String(description='Report title'),
    'file_path': fields.String(description='File path'),
    'file_size': fields.Integer(description='File size in bytes'),
    'start_date': fields.String(description='Start date'),
    'end_date': fields.String(description='End date'),
    'metadata': fields.Raw(description='Report metadata'),
    'created_at': fields.String(description='Creation timestamp')
})

report_list_model = reports_ns.model('ReportList', {
    'reports': fields.List(fields.Nested(report_model)),
    'total': fields.Integer(description='Total reports'),
    'page': fields.Integer(description='Current page'),
    'per_page': fields.Integer(description='Reports per page')
})


@reports_ns.route('/generate')
class GenerateReport(Resource):
    """Generate a new report."""
    
    @jwt_required()
    @reports_ns.expect(report_generation_model)
    @reports_ns.doc(security='Bearer Auth')
    @reports_ns.response(200, 'Report generated successfully', report_model)
    @reports_ns.response(400, 'Invalid request data')
    @reports_ns.response(401, 'Unauthorized')
    def post(self):
        """Generate a new report."""
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Debug logging
        print(f"Received report generation request: {data}")
        
        try:
            # Handle empty string dates from frontend
            if data.get('start_date') == '':
                data['start_date'] = None
            if data.get('end_date') == '':
                data['end_date'] = None
            
            # Validate request
            report_request = ReportGenerationRequest(**data)
            
            # Generate report
            report = ReportService.generate_report(
                user_id=user_id,
                report_type=report_request.report_type,
                start_date=report_request.start_date,
                end_date=report_request.end_date,
                include_charts=report_request.include_charts,
                title=report_request.title
            )
            
            return {
                'success': True,
                'message': 'Report generated successfully',
                'report': report
            }, 200
            
        except ValidationError as e:
            print(f"Validation error: {e.errors()}")
            return {
                'success': False,
                'message': 'Invalid request data',
                'errors': e.errors()
            }, 400
        except ValueError as e:
            print(f"Value error: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }, 400
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'Error generating report: {str(e)}'
            }, 500


@reports_ns.route('/list')
class ReportList(Resource):
    """List user's reports."""
    
    @jwt_required()
    @reports_ns.doc(security='Bearer Auth')
    @reports_ns.response(200, 'Reports retrieved successfully', report_list_model)
    @reports_ns.response(401, 'Unauthorized')
    def get(self):
        """Get list of user's generated reports."""
        user_id = get_jwt_identity()
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        try:
            reports_data = ReportService.get_user_reports(
                user_id=user_id,
                page=page,
                per_page=per_page
            )
            
            return {
                'success': True,
                **reports_data
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving reports: {str(e)}'
            }, 500


@reports_ns.route('/<string:report_id>')
class ReportDetail(Resource):
    """Get or delete a specific report."""
    
    @jwt_required()
    @reports_ns.doc(security='Bearer Auth')
    @reports_ns.response(200, 'Report retrieved successfully', report_model)
    @reports_ns.response(404, 'Report not found')
    @reports_ns.response(401, 'Unauthorized')
    def get(self, report_id):
        """Get report details."""
        user_id = get_jwt_identity()
        
        try:
            report = ReportService.get_report(report_id, user_id)
            
            if not report:
                return {
                    'success': False,
                    'message': 'Report not found'
                }, 404
            
            return {
                'success': True,
                'report': report
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving report: {str(e)}'
            }, 500
    
    @jwt_required()
    @reports_ns.doc(security='Bearer Auth')
    @reports_ns.response(200, 'Report deleted successfully')
    @reports_ns.response(404, 'Report not found')
    @reports_ns.response(401, 'Unauthorized')
    def delete(self, report_id):
        """Delete a report."""
        user_id = get_jwt_identity()
        
        try:
            success = ReportService.delete_report(report_id, user_id)
            
            if not success:
                return {
                    'success': False,
                    'message': 'Report not found'
                }, 404
            
            return {
                'success': True,
                'message': 'Report deleted successfully'
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deleting report: {str(e)}'
            }, 500


@reports_ns.route('/<string:report_id>/download')
class ReportDownload(Resource):
    """Download a report PDF."""
    
    @jwt_required()
    @reports_ns.doc(security='Bearer Auth')
    @reports_ns.response(200, 'Report PDF file')
    @reports_ns.response(404, 'Report not found')
    @reports_ns.response(401, 'Unauthorized')
    def get(self, report_id):
        """Download report PDF."""
        user_id = get_jwt_identity()
        
        try:
            report = ReportService.get_report(report_id, user_id)
            
            if not report:
                return {
                    'success': False,
                    'message': 'Report not found'
                }, 404
            
            file_path = report['file_path']
            
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'message': 'Report file not found on server'
                }, 404
            
            # Send file
            return send_file(
                file_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"{report['title'].replace(' ', '_')}.pdf"
            )
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error downloading report: {str(e)}'
            }, 500
