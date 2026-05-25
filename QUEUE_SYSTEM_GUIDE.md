# Queue System Implementation Guide

## Overview

The Excel verification project now uses an **asynchronous queue system** with:
- **RabbitMQ** as the message broker (queue management)
- **Redis** as the result backend (storing task results)
- **Celery** as the distributed task queue

This allows Excel files to be processed in the background without blocking the API, providing a much better user experience for large files.

## Architecture

```
User → Django API → RabbitMQ → Celery Worker → Redis (results)
                                     ↓
                                  Database
                                     ↓
                             Generated Files
```

## Prerequisites

### 1. RabbitMQ (Already Installed)
- **Service**: Should be running on `localhost:5672`
- **Default credentials**: `guest:guest`
- **Check status**:
  ```powershell
  # Check if RabbitMQ is running
  Get-Service -Name RabbitMQ
  ```

### 2. Redis (Already Installed)
- **Service**: Should be running on `localhost:6379`
- **Check status**:
  ```powershell
  # Check if Redis is running
  Get-Service -Name Redis
  ```

## Database Schema

### QueueJob Table

The `excel_processor_queuejob` table tracks all async jobs:

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | varchar(255) | Unique Celery task ID (UUID) |
| `filename` | varchar(255) | Original filename |
| `file_path` | varchar(500) | Path to uploaded file |
| `status` | varchar(20) | pending, queued, processing, completed, failed |
| `progress` | integer | Progress percentage (0-100) |
| `current_step` | varchar(100) | Current processing step description |
| `total_rows` | integer | Total rows in Excel |
| `valid_rows` | integer | Count of valid rows |
| `invalid_rows` | integer | Count of invalid rows |
| `error_count` | integer | Total error count |
| `output_file_path` | varchar(500) | Path to all records file |
| `good_records_file_path` | varchar(500) | Path to good records file |
| `rejected_records_file_path` | varchar(500) | Path to rejected records file |
| `validation_report_id` | integer | FK to ValidationReport |
| `excel_upload_id` | integer | FK to ExcelUpload |
| `error_message` | text | Error message if failed |
| `error_traceback` | text | Full error traceback |
| `created_at` | datetime | Job creation time |
| `started_at` | datetime | Job start time |
| `completed_at` | datetime | Job completion time |
| `processing_logs` | json | Array of timestamped log messages |

**Indexes:**
- `job_id` (unique)
- `status`
- `created_at` (desc)

## Starting the System

### 1. Start RabbitMQ (if not running)
```powershell
# Start RabbitMQ service
Start-Service RabbitMQ
```

### 2. Start Redis (if not running)
```powershell
# Start Redis service
Start-Service Redis
```

### 3. Start Django Server
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py runserver 8000
```

### 4. Start Celery Worker
In a **new terminal**:
```powershell
# From project root
.\start-celery.ps1
```

Or manually:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
celery -A backend worker --loglevel=info --pool=solo
```

**Note**: Use `--pool=solo` on Windows as the default pool doesn't work properly.

### 5. Start Frontend
```powershell
cd frontend
npm run dev
```

## API Flow

### 1. Upload and Map Headers (Same as Before)
```http
POST /api/excel-uploads/upload/
POST /api/excel-uploads/{id}/map_headers/
```

### 2. Queue Validation Task (New)
```http
POST /api/excel-uploads/{id}/validate/
```

**Response (202 Accepted)**:
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "queued",
  "message": "Validation task has been queued. Use the job_id to check progress.",
  "check_status_url": "/api/queue-jobs/a1b2c3d4-e5f6-7890-abcd-ef1234567890/status/"
}
```

### 3. Check Job Status (New)
```http
GET /api/queue-jobs/{job_id}/status/
```

**Response (Processing)**:
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "filename": "customers.xlsx",
  "status": "processing",
  "progress": 60,
  "current_step": "Generating all records file",
  "total_rows": 1000,
  "valid_rows": 850,
  "invalid_rows": 150,
  "error_count": 200,
  "created_at": "2026-05-13T12:00:00Z",
  "started_at": "2026-05-13T12:00:05Z",
  "completed_at": null
}
```

**Response (Completed)**:
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "filename": "customers.xlsx",
  "status": "completed",
  "progress": 100,
  "current_step": "Processing complete",
  "total_rows": 1000,
  "valid_rows": 850,
  "invalid_rows": 150,
  "error_count": 200,
  "created_at": "2026-05-13T12:00:00Z",
  "started_at": "2026-05-13T12:00:05Z",
  "completed_at": "2026-05-13T12:01:30Z",
  "files": {
    "all_records": "validated/2026/05/13/verified_customers.xlsx",
    "good_records": "validated/good/2026/05/13/good_records_customers.xlsx",
    "rejected_records": "validated/rejected/2026/05/13/rejected_records_customers.xlsx"
  },
  "validation_summary": {
    "total_rows": 1000,
    "valid_rows": 850,
    "invalid_rows": 150,
    "error_count": 200
  },
  "status_message": "Processed"
}
```

### 4. Get Job Logs (New)
```http
GET /api/queue-jobs/{job_id}/logs/
```

**Response**:
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "logs": [
    {
      "timestamp": "2026-05-13T12:00:05.123Z",
      "level": "info",
      "message": "Job created and queued for processing"
    },
    {
      "timestamp": "2026-05-13T12:00:06.456Z",
      "level": "info",
      "message": "Started processing Excel file"
    },
    {
      "timestamp": "2026-05-13T12:00:15.789Z",
      "level": "info",
      "message": "Successfully loaded 1000 rows from Excel"
    },
    {
      "timestamp": "2026-05-13T12:01:30.012Z",
      "level": "success",
      "message": "Processing completed successfully"
    }
  ]
}
```

### 5. Download Files (Same as Before)
```http
GET /api/excel-uploads/{id}/download/
GET /api/excel-uploads/{id}/download_good_records/
GET /api/excel-uploads/{id}/download_rejected_records/
```

## Processing Steps and Progress

| Progress | Step | Description |
|----------|------|-------------|
| 0% | pending | Job created |
| 10% | Reading Excel file | Loading file from disk |
| 20% | Loaded X rows | File loaded into memory |
| 30% | Running validation rules | Applying regex and validation |
| 40% | Validation complete | Validation results ready |
| 50% | Generating output files | Creating Excel files |
| 60% | Generating all records file | Creating main output file |
| 70% | Generating good and rejected files | Creating separate files |
| 90% | Finalizing | Saving paths to database |
| 100% | Processing complete | All done |

## Job Status States

1. **pending**: Job created but not yet queued
2. **queued**: Job submitted to RabbitMQ, waiting for worker
3. **processing**: Worker is actively processing the file
4. **completed**: Processing finished successfully
5. **failed**: Processing failed with error

## Error Handling

If a job fails:

**Response**:
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "failed",
  "error_message": "File not found: /path/to/file.xlsx",
  "...": "..."
}
```

The full traceback is stored in `error_traceback` field for debugging.

## Monitoring

### Check Celery Worker Status
```powershell
celery -A backend inspect active
```

### Check Queue Size
```powershell
celery -A backend inspect reserved
```

### Purge Queue (Clear all tasks)
```powershell
celery -A backend purge
```

## Configuration

### Celery Settings (in settings.py)

```python
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'  # RabbitMQ
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Redis
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_RESULT_EXPIRES = 3600  # 1 hour
```

## Frontend Integration (To Do)

Update frontend to:
1. Get `job_id` from validate response
2. Poll `/api/queue-jobs/{job_id}/status/` every 2-3 seconds
3. Show progress bar with `progress` percentage
4. Display `current_step` to user
5. When `status === 'completed'`, show download buttons
6. If `status === 'failed'`, show error message

## Benefits

✅ **Non-blocking**: API responds immediately  
✅ **Scalable**: Multiple workers can process jobs in parallel  
✅ **Progress tracking**: Real-time updates on processing status  
✅ **Fault tolerant**: Jobs are retried if worker crashes  
✅ **Better UX**: Users don't wait for large files to process  
✅ **Detailed logs**: Full processing log for each job  
✅ **Queue management**: Jobs are processed in order

## Troubleshooting

### Worker not processing jobs
```powershell
# Check if worker is running
celery -A backend inspect ping

# Check RabbitMQ connection
telnet localhost 5672
```

### Redis connection issues
```powershell
# Test Redis connection
redis-cli ping
# Should return: PONG
```

### View task details in Celery
```powershell
celery -A backend inspect query_task <task_id>
```

## Production Considerations

For production deployment:
1. Use a process manager (Supervisor, systemd) to keep Celery workers running
2. Scale workers based on load
3. Use Flower for monitoring: `celery -A backend flower`
4. Set up proper logging and error tracking
5. Configure task retries for transient failures
6. Consider using separate queues for different priority levels
