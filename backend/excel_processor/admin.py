from django.contrib import admin
from .models import ExcelUpload, HeaderMappingTemplate, ValidationRule, ValidationReport

@admin.register(ExcelUpload)
class ExcelUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_filename', 'uploaded_at', 'session_key')
    list_filter = ('uploaded_at',)
    search_fields = ('original_filename', 'session_key')

@admin.register(HeaderMappingTemplate)
class HeaderMappingTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'template_name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('template_name',)

@admin.register(ValidationRule)
class ValidationRuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'rule_type', 'field_name', 'is_active')
    list_filter = ('rule_type', 'is_active')
    search_fields = ('field_name',)

@admin.register(ValidationReport)
class ValidationReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'excel_upload', 'valid_rows_count', 'invalid_rows_count', 'created_at')
    list_filter = ('created_at',)
