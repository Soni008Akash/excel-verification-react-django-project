# Migration Guide: Errors in Excel File

## Changes Made

### 1. ✅ Database Changed to PostgreSQL
- Updated `settings.py` to use PostgreSQL database `excel_verification`
- Added `psycopg2` to `requirements.txt`
- See [DATABASE_SETUP.md](DATABASE_SETUP.md) for setup instructions

### 2. ✅ Errors Now in Excel File
- **Before**: Errors displayed on the verification page
- **After**: Errors included as comma-separated values in a "Validation Errors" column in the Excel file

### 3. ✅ Frontend Simplified
- Removed detailed error list display
- Removed data preview table
- Shows only summary statistics and download button
- Users download Excel file to see all errors

### 4. ✅ Excel File Format
The downloaded Excel file now contains:
- All original data with mapped headers
- **New column**: "Validation Errors" (last column)
  - Empty for valid rows
  - Comma-separated error messages for invalid rows
  - Format: `Column: Issue, Column: Issue`
  - Example: `Mobile Number: Invalid Mobile number (various formats), Email: Invalid Email address`
- Color-coded rows (red = has errors)
- No separate validation report sheet

## Example Excel Output

| Name | Mobile | Email | Customer ID | Validation Errors |
|------|--------|-------|-------------|-------------------|
| John Doe | 1234567890 | john@example.com | CUST001 | |
| Jane Smith | invalid | jane@example.com | CUST002 | Mobile: Invalid Mobile number (various formats) |
| Bob Johnson | 5551234567 | not_email | CUST@03 | Email: Invalid Email address, Customer ID: Invalid Alphanumeric |

## Setup Steps

### 1. Install PostgreSQL Client
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install psycopg2
```

If installation fails on Windows, use psycopg2-binary:
```powershell
pip install psycopg2-binary
```

### 2. Configure Database
Update `backend/backend/settings.py` with your PostgreSQL credentials:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'excel_verification',
        'USER': 'postgres',  # Your PostgreSQL username
        'PASSWORD': '',  # Your PostgreSQL password
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. Run Migrations
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py migrate
```

### 4. Rebuild Frontend (if needed)
```powershell
cd frontend
npm run build
```

### 5. Restart Servers
```powershell
# Stop current servers (Ctrl+C in each terminal)
# Then restart
.\start-dev.ps1
```

## Testing

1. Open http://localhost:5173
2. Upload an Excel file
3. Map headers and select validation rules
4. Click "Next: Verify Data"
5. You'll see summary statistics (total rows, valid rows, errors)
6. Click "Download Verified Excel"
7. Open the downloaded file
8. Check the "Validation Errors" column (last column)
9. Rows with errors will be highlighted in red

## Benefits

✅ **Cleaner UI** - No cluttered error lists on the page  
✅ **Better for Large Files** - All errors in Excel, not overwhelming the browser  
✅ **Easier Review** - Users can filter/sort errors in Excel  
✅ **Permanent Record** - Errors saved in downloadable file  
✅ **Database Tracking** - All validations stored in PostgreSQL for reporting

## Files Modified

**Backend:**
- `backend/settings.py` - PostgreSQL configuration
- `backend/requirements.txt` - Added psycopg2
- `backend/excel_processor/utils.py` - Modified Excel generation to add errors column
- `backend/excel_processor/views.py` - Removed error/preview data from API response

**Frontend:**
- `frontend/src/pages/VerifyPage.jsx` - Simplified to show summary only
- `frontend/src/pages/VerifyPage.css` - Updated styles

**Documentation:**
- `DATABASE_SETUP.md` (NEW) - MySQL setup guide
- `MIGRATION_GUIDE.md` (NEW) - This file
- `README.md` - Updated database section
