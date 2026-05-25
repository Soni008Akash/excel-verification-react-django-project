# Database Setup Instructions

## Step 1: Install PostgreSQL Client

The project uses PostgreSQL database. Install the PostgreSQL client library:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install psycopg2
```

### Windows Installation

If you get an error installing psycopg2, you may need to:

1. **Use psycopg2-binary** (easier installation):
   ```powershell
   pip install psycopg2-binary
   ```

## Step 2: Database Configuration

The database is configured in `backend/backend/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'excel_verification',
        'USER': 'postgres',
        'PASSWORD': '12345',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**Update the USER and PASSWORD** fields with your PostgreSQL credentials.

## Step 3: Database Already Created

You mentioned you've already created the `excel_verification` database. If not, create it:

```sql
CREATE DATABASE excel_verification;
```

## Step 4: Run Migrations

Run Django migrations to create the required tables:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py migrate
```

This will create the following tables:
- `excel_processor_excelupload` - Stores uploaded Excel files
- `excel_processor_headermappingtemplate` - Stores header mapping templates
- `excel_processor_validationrule` - Stores validation rules
- `excel_processor_validationreport` - Stores validation reports
- Plus Django's default tables (auth, sessions, etc.)

## Step 5: Verify Database Connection

Test the connection:

```powershell
python manage.py dbshell
```

This should open a PostgreSQL shell connected to your database.

## Troubleshooting

### Error: "connection to server failed"
- Make sure PostgreSQL service is running
- Check hostname, port, username, and password in settings.py

### Error: "fe_sendauth: no password supplied"
- Verify PostgreSQL password is correctly set in settings.py

### Error: "database does not exist"
- Create the database: `CREATE DATABASE excel_verification;`

## Tables Created

After running migrations, these tables will be in your database:

1. **excel_processor_excelupload**
   - id
   - file
   - original_filename
   - uploaded_at
   - session_key
   - original_headers (JSON)
   - mapped_headers (JSON)
   - validation_rules (JSON)

2. **excel_processor_headermappingtemplate**
   - id
   - template_name
   - original_headers (JSON)
   - mapped_headers (JSON)
   - created_at
   - updated_at

3. **excel_processor_validationrule**
   - id
   - rule_type
   - field_name
   - rule_config (JSON)
   - is_active
   - created_at

4. **excel_processor_validationreport**
   - id
   - excel_upload_id (Foreign Key)
   - errors (JSON)
   - warnings (JSON)
   - valid_rows_count
   - invalid_rows_count
   - created_at
