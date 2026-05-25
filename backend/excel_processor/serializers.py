from rest_framework import serializers
from .models import ExcelUpload, HeaderMappingTemplate, ValidationRule, ValidationReport, QueueJob


class ExcelUploadSerializer(serializers.ModelSerializer):
    """Serializer for Excel file uploads"""
    
    class Meta:
        model = ExcelUpload
        fields = ['id', 'file', 'original_filename', 'uploaded_at', 'session_key', 
                  'original_headers', 'mapped_headers']
        read_only_fields = ['id', 'uploaded_at', 'session_key', 'original_headers']


class HeaderMappingTemplateSerializer(serializers.ModelSerializer):
    """Serializer for header mapping templates"""
    
    class Meta:
        model = HeaderMappingTemplate
        fields = ['id', 'template_name', 'original_headers', 'mapped_headers', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ValidationRuleSerializer(serializers.ModelSerializer):
    """Serializer for validation rules"""
    
    class Meta:
        model = ValidationRule
        fields = ['id', 'rule_type', 'field_name', 'rule_config', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ValidationReportSerializer(serializers.ModelSerializer):
    """Serializer for validation reports"""
    excel_upload_filename = serializers.CharField(source='excel_upload.original_filename', read_only=True)
    
    class Meta:
        model = ValidationReport
        fields = ['id', 'excel_upload', 'excel_upload_filename', 'errors', 'warnings', 
                  'valid_rows_count', 'invalid_rows_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class QueueJobSerializer(serializers.ModelSerializer):
    """Serializer for queue jobs"""
    
    class Meta:
        model = QueueJob
        fields = ['job_id', 'filename', 'file_path', 'status', 'progress', 'current_step',
                  'total_rows', 'valid_rows', 'invalid_rows', 'error_count',
                  'output_file_path', 'good_records_file_path', 'rejected_records_file_path',
                  'error_message', 'processing_logs',
                  'created_at', 'started_at', 'completed_at']
        read_only_fields = ['job_id', 'created_at', 'started_at', 'completed_at']

