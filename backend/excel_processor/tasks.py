""" 
Celery tasks for async Excel processing
"""
import os
import traceback
from datetime import datetime
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.core.files import File
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import pandas as pd

from .models import QueueJob, ExcelUpload, ValidationReport
from .validators import validate_excel_data
from .utils import generate_validated_excel, generate_good_and_rejected_files


def send_job_progress(job_id, status, progress, current_step='', **kwargs):
    """
    Send job progress update via WebSocket
    
    Args:
        job_id: Job ID (UUID string)
        status: Job status (pending/queued/processing/completed/failed)
        progress: Progress percentage (0-100)
        current_step: Current processing step description
        **kwargs: Additional data (total_rows, valid_rows, invalid_rows, error_count, error_message)
    """
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f'job_{job_id}',
                {
                    'type': 'job_progress',  # Changed from 'job.progress' to 'job_progress'
                    'job_id': str(job_id),
                    'status': status,
                    'progress': progress,
                    'current_step': current_step,
                    'timestamp': datetime.now().isoformat(),
                    **kwargs
                }
            )
            print(f"[WebSocket] Sent progress update: {progress}% - {current_step}")
        else:
            print("[WebSocket] Channel layer not available")
    except Exception as e:
        print(f"[WebSocket] Error sending progress: {e}")
        import traceback
        traceback.print_exc()


@shared_task(bind=True, name='excel_processor.process_excel_validation')
def process_excel_validation(self, job_id, excel_upload_id):
    """
    Async task to process Excel validation
    
    Args:
        job_id: QueueJob ID
        excel_upload_id: ExcelUpload ID
    """
    job = None
    try:
        # Get the job and upload
        job = QueueJob.objects.get(job_id=job_id)
        excel_upload = ExcelUpload.objects.get(id=excel_upload_id)
        
        # Update job status
        job.status = 'processing'
        job.started_at = timezone.now()
        job.progress = 10
        job.current_step = 'Reading Excel file'
        job.add_log('Started processing Excel file', 'info')
        job.save()
        
        # Send WebSocket update
        send_job_progress(job_id, 'processing', 10, 'Reading Excel file')
        
        # Read Excel data
        if excel_upload.file.path.endswith('.csv'):
            df = pd.read_csv(excel_upload.file.path)
        else:
            df = pd.read_excel(excel_upload.file.path, engine='openpyxl')
        
        job.total_rows = len(df)
        job.progress = 20
        job.current_step = f'Loaded {len(df)} rows'
        job.add_log(f'Successfully loaded {len(df)} rows from Excel', 'info')
        job.save()
        
        # Send WebSocket update
        send_job_progress(job_id, 'processing', 20, f'Loaded {len(df)} rows', total_rows=len(df))
        
        # Run validation
        job.progress = 30
        job.current_step = 'Running validation rules'
        job.add_log('Applying validation rules', 'info')
        job.save()
        
        # Send WebSocket update
        send_job_progress(job_id, 'processing', 30, 'Running validation rules', total_rows=len(df))
        
        validation_results = validate_excel_data(
            df,
            excel_upload.mapped_headers,
            excel_upload.validation_rules,
            excel_upload.validation_options
        )
        
        # Update counts
        job.valid_rows = validation_results['valid_rows_count']
        job.invalid_rows = validation_results['invalid_rows_count']
        job.error_count = len(validation_results['errors'])
        job.progress = 40
        job.current_step = f'Validation complete: {job.valid_rows} valid, {job.invalid_rows} invalid'
        job.add_log(f'Validation complete: {job.valid_rows} valid rows, {job.invalid_rows} invalid rows', 'info')
        job.save()
        
        # Send WebSocket update
        send_job_progress(job_id, 'processing', 40, f'Validation complete: {job.valid_rows} valid, {job.invalid_rows} invalid', 
                         total_rows=job.total_rows, valid_rows=job.valid_rows, invalid_rows=job.invalid_rows, error_count=job.error_count)
        
        # Create validation report
        report = ValidationReport.objects.create(
            excel_upload=excel_upload,
            errors=validation_results['errors'],
            warnings=validation_results['warnings'],
            valid_rows_count=validation_results['valid_rows_count'],
            invalid_rows_count=validation_results['invalid_rows_count']
        )
        
        job.validation_report = report
        job.progress = 50
        job.current_step = 'Generating output files'
        job.add_log('Creating output Excel files', 'info')
        job.save()
        
        # Send WebSocket update
        send_job_progress(job_id, 'processing', 50, 'Generating output files', 
                         total_rows=job.total_rows, valid_rows=job.valid_rows, invalid_rows=job.invalid_rows)
        
        # Generate output files
        output_filename = f"verified_{excel_upload.original_filename}"
        output_path = os.path.join(
            settings.MEDIA_ROOT,
            'validated',
            excel_upload.uploaded_at.strftime('%Y/%m/%d'),
            output_filename
        )
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        validation_report_data = {
            'errors': report.errors,
            'warnings': report.warnings,
            'valid_rows_count': report.valid_rows_count,
            'invalid_rows_count': report.invalid_rows_count
        }
        
        # Generate all records file
        job.progress = 60
        job.current_step = 'Generating all records file'
        job.add_log('Generating file with all records', 'info')
        job.save()
        
        # Send WebSocket update
        send_job_progress(job_id, 'processing', 60, 'Generating all records file', 
                         total_rows=job.total_rows, valid_rows=job.valid_rows, invalid_rows=job.invalid_rows)
        
        generate_validated_excel(
            excel_upload.file.path,
            excel_upload.mapped_headers,
            validation_report_data,
            output_path
        )
        
        # Save output file to FileField properly
        with open(output_path, 'rb') as f:
            report.output_file.save(
                output_filename,
                File(f),
                save=False
            )
        
        job.output_file_path = report.output_file.name
        
        # Generate separate good and rejected files
        job.progress = 70
        job.current_step = 'Generating good and rejected records files'
        job.add_log('Generating separate files for good and rejected records', 'info')
        job.save()
        
        # Send WebSocket update
        send_job_progress(job_id, 'processing', 70, 'Generating good and rejected records files', 
                         total_rows=job.total_rows, valid_rows=job.valid_rows, invalid_rows=job.invalid_rows)
        
        good_filename = f"good_records_{excel_upload.original_filename}"
        rejected_filename = f"rejected_records_{excel_upload.original_filename}"
        
        good_path = os.path.join(
            settings.MEDIA_ROOT,
            'validated/good',
            excel_upload.uploaded_at.strftime('%Y/%m/%d'),
            good_filename
        )
        rejected_path = os.path.join(
            settings.MEDIA_ROOT,
            'validated/rejected',
            excel_upload.uploaded_at.strftime('%Y/%m/%d'),
            rejected_filename
        )
        
        os.makedirs(os.path.dirname(good_path), exist_ok=True)
        os.makedirs(os.path.dirname(rejected_path), exist_ok=True)
        
        generate_good_and_rejected_files(
            excel_upload.file.path,
            excel_upload.mapped_headers,
            validation_report_data,
            good_path,
            rejected_path,
            excel_upload.validation_options
        )
        
        # Save files to FileField properly
        with open(good_path, 'rb') as f:
            report.good_records_file.save(
                good_filename,
                File(f),
                save=False
            )
        
        with open(rejected_path, 'rb') as f:
            report.rejected_records_file.save(
                rejected_filename,
                File(f),
                save=False
            )
        
        job.good_records_file_path = report.good_records_file.name
        job.rejected_records_file_path = report.rejected_records_file.name
        
        # Determine status
        job.progress = 90
        job.current_step = 'Finalizing'
        job.save()
        
        # Send WebSocket update
        send_job_progress(job_id, 'processing', 90, 'Finalizing', 
                         total_rows=job.total_rows, valid_rows=job.valid_rows, invalid_rows=job.invalid_rows)
        
        if validation_results['valid_rows_count'] == 0 and validation_results['invalid_rows_count'] > 0:
            report.status = 2  # All rejected
        elif validation_results['invalid_rows_count'] == 0:
            report.status = 1  # All valid
        else:
            report.status = 1  # Mixed
        
        report.save()
        
        # Mark job as completed
        job.status = 'completed'
        job.progress = 100
        job.current_step = 'Processing complete'
        job.completed_at = timezone.now()
        job.add_log('Processing completed successfully', 'success')
        job.save()
        
        # Send WebSocket completion message
        send_job_progress(job_id, 'completed', 100, 'Processing complete', 
                         total_rows=job.total_rows, valid_rows=job.valid_rows, 
                         invalid_rows=job.invalid_rows, error_count=job.error_count)
        
        return {
            'status': 'completed',
            'job_id': job_id,
            'total_rows': job.total_rows,
            'valid_rows': job.valid_rows,
            'invalid_rows': job.invalid_rows
        }
        
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        if job:
            job.status = 'failed'
            job.error_message = error_msg
            job.error_traceback = error_trace
            job.completed_at = timezone.now()
            job.add_log(f'Processing failed: {error_msg}', 'error')
            job.save()
            
            # Send WebSocket failure message
            send_job_progress(job_id, 'failed', job.progress or 0, 'Processing failed', 
                             error_message=error_msg)
        
        # Re-raise to mark task as failed in Celery
        raise
