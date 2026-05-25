from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
import os
import uuid

from .models import ExcelUpload, HeaderMappingTemplate, ValidationRule, ValidationReport, QueueJob
from .serializers import (
    ExcelUploadSerializer, 
    HeaderMappingTemplateSerializer,
    ValidationRuleSerializer,
    ValidationReportSerializer
)
from .utils import extract_headers_from_excel, infer_data_types, generate_validated_excel, generate_good_and_rejected_files, get_preview_data
from .validators import validate_excel_data, get_available_regex_patterns
import pandas as pd


class ExcelUploadViewSet(viewsets.ModelViewSet):
    """ViewSet for Excel file upload and processing"""
    queryset = ExcelUpload.objects.all()
    serializer_class = ExcelUploadSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    @action(detail=False, methods=['get'])
    def regex_patterns(self, request):
        """
        Get available regex patterns for validation
        GET /api/excel-uploads/regex_patterns/
        """
        patterns = get_available_regex_patterns()
        return Response(patterns, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload(self, request):
        """
        Upload Excel file and extract headers
        POST /api/upload/
        """
        try:
            file = request.FILES.get('file')
            if not file:
                return Response(
                    {'error': 'No file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate file extension
            allowed_extensions = ['.xlsx', '.xls', '.csv']
            file_ext = os.path.splitext(file.name)[1].lower()
            if file_ext not in allowed_extensions:
                return Response(
                    {'error': f'File type not supported. Allowed: {", ".join(allowed_extensions)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create ExcelUpload instance
            excel_upload = ExcelUpload.objects.create(
                file=file,
                original_filename=file.name,
                session_key=request.session.session_key or request.session.create()
            )
            
            # Extract headers
            try:
                headers, df = extract_headers_from_excel(excel_upload.file.path)
                data_types = infer_data_types(df)
                
                # Store headers in model
                excel_upload.original_headers = headers
                excel_upload.save()
                
                # Prepare response with headers and data types
                headers_with_types = [
                    {
                        'original': header,
                        'dataType': data_types.get(header, 'text')
                    }
                    for header in headers
                ]
                
                return Response({
                    'file_id': excel_upload.pk,
                    'filename': excel_upload.original_filename,
                    'headers': headers_with_types,
                    'row_count': len(df)
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                # Delete the upload if processing fails
                excel_upload.delete()
                return Response(
                    {'error': f'Error processing file: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def map_headers(self, request, pk=None):
        """
        Save header mappings, validation rules, and validation options for uploaded file
        POST /api/excel-uploads/{id}/map_headers/
        Body: { 
            "mappings": { "old_header": "new_header", ... },
            "validation_rules": { "old_header": "mobile|email|alphanumeric|string_only|numeric_only|pincode|none", ... },
            "validation_options": { "check_duplicates": true, "check_empty_values": true }
        }
        """
        try:
            excel_upload = self.get_object()
            mappings = request.data.get('mappings', {})
            validation_rules = request.data.get('validation_rules', {})
            validation_options = request.data.get('validation_options', {'check_duplicates': True, 'check_empty_values': True})
            
            if not mappings:
                return Response(
                    {'error': 'No mappings provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save mappings, validation rules, and options
            excel_upload.mapped_headers = mappings
            excel_upload.validation_rules = validation_rules
            excel_upload.validation_options = validation_options
            excel_upload.save()
            
            return Response({
                'message': 'Header mappings, validation rules, and options saved successfully',
                'file_id': excel_upload.pk,
                'mappings': mappings,
                'validation_rules': validation_rules,
                'validation_options': validation_options
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """
        Queue Excel validation task for async processing
        POST /api/excel-uploads/{id}/validate/
        """
        try:
            from .tasks import process_excel_validation
            
            excel_upload = self.get_object()
            
            if not excel_upload.mapped_headers:
                return Response(
                    {'error': 'Headers not mapped yet'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create a unique job ID
            job_id = str(uuid.uuid4())
            
            # Create queue job record
            queue_job = QueueJob.objects.create(
                job_id=job_id,
                filename=excel_upload.original_filename,
                file_path=excel_upload.file.path,
                status='queued',
                excel_upload=excel_upload
            )
            queue_job.add_log('Job created and queued for processing', 'info')
            
            # Queue the task to Celery
            task = process_excel_validation.apply_async(
                args=[job_id, excel_upload.pk],
                task_id=job_id
            )
            
            return Response({
                'job_id': job_id,
                'status': 'queued',
                'message': 'Validation task has been queued. Use the job_id to check progress.',
                'check_status_url': f'/api/queue-jobs/{job_id}/status/'
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Download cached validated Excel file (generated during validation)
        GET /api/excel-uploads/{id}/download/
        """
        try:
            excel_upload = self.get_object()
            
            # Get latest validation report
            report = excel_upload.validation_reports.first()
            if not report:
                return Response(
                    {'error': 'No validation report found. Please validate first.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if output file exists
            if not report.output_file:
                return Response(
                    {'error': 'Validated file not found. Please run validation again.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Serve the pre-generated cached file
            output_filename = f"verified_{excel_upload.original_filename}"
            
            # Return cached file - much faster!
            response = FileResponse(
                open(report.output_file.path, 'rb'),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{output_filename}"'
            
            return response
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download_good_records(self, request, pk=None):
        """
        Download good/valid records only
        GET /api/excel-uploads/{id}/download_good_records/
        """
        try:
            excel_upload = self.get_object()
            
            # Get latest validation report
            report = excel_upload.validation_reports.first()
            if not report:
                return Response(
                    {'error': 'No validation report found. Please validate first.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if good records file exists
            if not report.good_records_file:
                return Response(
                    {'error': 'Good records file not found. Please run validation again.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Serve the good records file
            good_filename = f"good_records_{excel_upload.original_filename}"
            
            response = FileResponse(
                open(report.good_records_file.path, 'rb'),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{good_filename}"'
            
            return response
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download_rejected_records(self, request, pk=None):
        """
        Download rejected records only (with error messages)
        GET /api/excel-uploads/{id}/download_rejected_records/
        """
        try:
            excel_upload = self.get_object()
            
            # Get latest validation report
            report = excel_upload.validation_reports.first()
            if not report:
                return Response(
                    {'error': 'No validation report found. Please validate first.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if rejected records file exists
            if not report.rejected_records_file:
                return Response(
                    {'error': 'Rejected records file not found. Please run validation again.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Serve the rejected records file
            rejected_filename = f"rejected_records_{excel_upload.original_filename}"
            
            response = FileResponse(
                open(report.rejected_records_file.path, 'rb'),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{rejected_filename}"'
            
            return response
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QueueJobViewSet(viewsets.ViewSet):
    """ViewSet for queue job management and status checking"""
    
    @action(detail=False, methods=['get'], url_path='(?P<job_id>[^/.]+)/status')
    def status(self, request, job_id=None):
        """
        Get job status and progress
        GET /api/queue-jobs/{job_id}/status/
        """
        try:
            job = QueueJob.objects.get(job_id=job_id)
            
            response_data = {
                'job_id': job.job_id,
                'filename': job.filename,
                'status': job.status,
                'progress': job.progress,
                'current_step': job.current_step,
                'total_rows': job.total_rows,
                'valid_rows': job.valid_rows,
                'invalid_rows': job.invalid_rows,
                'error_count': job.error_count,
                'created_at': job.created_at.isoformat() if job.created_at else None,
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            }
            
            # Include file paths if completed
            if job.status == 'completed':
                response_data['files'] = {
                    'all_records': job.output_file_path,
                    'good_records': job.good_records_file_path,
                    'rejected_records': job.rejected_records_file_path,
                }
                if job.validation_report:
                    response_data['validation_summary'] = {
                        'total_rows': job.total_rows,
                        'valid_rows': job.valid_rows,
                        'invalid_rows': job.invalid_rows,
                        'error_count': job.error_count,
                    }
                    response_data['status_message'] = job.validation_report.get_status_display()
            
            # Include error details if failed
            if job.status == 'failed':
                response_data['error_message'] = job.error_message
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except QueueJob.DoesNotExist:
            return Response(
                {'error': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='(?P<job_id>[^/.]+)/logs')
    def logs(self, request, job_id=None):
        """
        Get job processing logs
        GET /api/queue-jobs/{job_id}/logs/
        """
        try:
            job = QueueJob.objects.get(job_id=job_id)
            
            return Response({
                'job_id': job.job_id,
                'logs': job.processing_logs if isinstance(job.processing_logs, list) else []
            }, status=status.HTTP_200_OK)
            
        except QueueJob.DoesNotExist:
            return Response(
                {'error': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HeaderMappingTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for header mapping templates"""
    queryset = HeaderMappingTemplate.objects.all()
    serializer_class = HeaderMappingTemplateSerializer
    
    @action(detail=False, methods=['post'])
    def save_template(self, request):
        """
        Save a new mapping template
        POST /api/mapping-templates/save_template/
        Body: {
            "template_name": "My Template",
            "original_headers": [...],
            "mapped_headers": {...}
        }
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ValidationRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for validation rules"""
    queryset = ValidationRule.objects.all()
    serializer_class = ValidationRuleSerializer


class ValidationReportViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for validation reports (read-only)"""
    queryset = ValidationReport.objects.all()
    serializer_class = ValidationReportSerializer
