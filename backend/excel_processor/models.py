from django.db import models
import json


class QueueJob(models.Model):
    """Model to track async job processing"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    job_id = models.CharField(max_length=255, unique=True, db_index=True, help_text='Celery task ID')
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    
    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    progress = models.IntegerField(default=0, help_text='Progress percentage (0-100)')
    current_step = models.CharField(max_length=100, blank=True, help_text='Current processing step')
    
    # Results and counts
    total_rows = models.IntegerField(default=0)
    valid_rows = models.IntegerField(default=0)
    invalid_rows = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    
    # File paths for generated files
    output_file_path = models.CharField(max_length=500, blank=True, null=True, help_text='Path to all records file')
    good_records_file_path = models.CharField(max_length=500, blank=True, null=True, help_text='Path to good records file')
    rejected_records_file_path = models.CharField(max_length=500, blank=True, null=True, help_text='Path to rejected records file')
    
    # Validation report reference
    validation_report = models.ForeignKey('ValidationReport', on_delete=models.SET_NULL, blank=True, null=True, related_name='queue_jobs')
    excel_upload = models.ForeignKey('ExcelUpload', on_delete=models.CASCADE, related_name='queue_jobs')
    
    # Error tracking
    error_message = models.TextField(blank=True, null=True)
    error_traceback = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Processing logs (JSON)
    processing_logs = models.JSONField(default=list, blank=True, help_text='Array of log messages with timestamps')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['job_id']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]
        
    def __str__(self):
        return f"Job {self.job_id} - {self.filename} ({self.status})"
    
    def add_log(self, message, level='info'):
        """Add a log entry to processing_logs"""
        from django.utils import timezone
        log_entry = {
            'timestamp': timezone.now().isoformat(),
            'level': level,
            'message': message
        }
        if not isinstance(self.processing_logs, list):
            self.processing_logs = []
        self.processing_logs.append(log_entry)
        self.save(update_fields=['processing_logs'])


class ExcelUpload(models.Model):
    """Model to store uploaded Excel files"""
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    original_filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    original_headers = models.JSONField(default=list, blank=True)
    mapped_headers = models.JSONField(default=dict, blank=True)
    validation_rules = models.JSONField(default=dict, blank=True, help_text='Regex validation rules per column')
    validation_options = models.JSONField(default=dict, blank=True, help_text='Validation options like check_duplicates, check_empty_values')
    
    class Meta:
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return f"{self.original_filename} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"


class HeaderMappingTemplate(models.Model):
    """Model to store reusable header mapping templates"""
    template_name = models.CharField(max_length=255, unique=True)
    original_headers = models.JSONField(default=list)
    mapped_headers = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.template_name


class ValidationRule(models.Model):
    """Model to store validation rules"""
    RULE_TYPE_CHOICES = [
        ('data_type', 'Data Type Validation'),
        ('required', 'Required Field'),
        ('business', 'Business Rule'),
    ]
    
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES)
    field_name = models.CharField(max_length=255, blank=True)
    rule_config = models.JSONField(default=dict, help_text='Configuration for the validation rule')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['rule_type', 'field_name']
        
    def __str__(self):
        return f"{self.get_rule_type_display()} - {self.field_name or 'Global'}"


class ValidationReport(models.Model):
    """Model to store validation results"""
    STATUS_CHOICES = [
        (0, 'Pending'),
        (1, 'Processed'),
        (2, 'All Rejected'),
    ]
    
    excel_upload = models.ForeignKey(ExcelUpload, on_delete=models.CASCADE, related_name='validation_reports')
    errors = models.JSONField(default=list)
    warnings = models.JSONField(default=list)
    valid_rows_count = models.IntegerField(default=0)
    invalid_rows_count = models.IntegerField(default=0)
    output_file = models.FileField(upload_to='validated/%Y/%m/%d/', blank=True, null=True, help_text='Pre-generated validated Excel file for fast download')
    good_records_file = models.FileField(upload_to='validated/good/%Y/%m/%d/', blank=True, null=True, help_text='Excel file with only valid/good records')
    rejected_records_file = models.FileField(upload_to='validated/rejected/%Y/%m/%d/', blank=True, null=True, help_text='Excel file with only rejected records and errors')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, help_text='0=Pending, 1=Processed, 2=All Rejected')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Report for {self.excel_upload.original_filename} - {self.valid_rows_count} valid, {self.invalid_rows_count} invalid"
