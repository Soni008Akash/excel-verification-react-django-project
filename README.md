# Excel Verify Project - Setup and Deployment Guide

## Prerequisites
- Python 3.8+
- Node.js 18+
- nginx (already installed at C://)

## Project Structure
```
ExcelVerifyProject/
├── backend/                 # Django backend
│   ├── backend/            # Django project settings
│   ├── excel_processor/    # Main app
│   ├── media/              # Uploaded files
│   ├── manage.py
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   ├── package.json
│   └── vite.config.js
└── nginx.conf             # nginx configuration
```

## Setup Instructions

### 1. Backend Setup (Django)

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional, for admin access)
python manage.py createsuperuser

# Create media directories
New-Item -ItemType Directory -Force -Path "media\uploads"

# Collect static files
python manage.py collectstatic --noinput

# Run development server
python manage.py runserver 8000
```

### 2. Frontend Setup (React)

```powershell
# Navigate to frontend directory (new terminal)
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# For production build
npm run build
```

### 3. nginx Configuration

```powershell
# Copy React build to nginx html folder
# First, build the React app
cd frontend
npm run build

# Copy build files to nginx
$nginxPath = "C:\nginx\html\excel-verify"
New-Item -ItemType Directory -Force -Path $nginxPath
Copy-Item -Path "dist\*" -Destination $nginxPath -Recurse -Force

# Copy nginx configuration
Copy-Item -Path "..\nginx.conf" -Destination "C:\nginx\conf\nginx.conf" -Force

# Test nginx configuration
cd C:\nginx
.\nginx.exe -t

# Start nginx (if not running)
Start-Process -FilePath "C:\nginx\nginx.exe"

# Reload nginx (if already running)
.\nginx.exe -s reload

# Stop nginx
.\nginx.exe -s stop
```

## Running the Application

### Development Mode

1. **Start Django backend** (Terminal 1):
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   python manage.py runserver 8000
   ```

2. **Start React frontend** (Terminal 2):
   ```powershell
   cd frontend
   npm run dev
   ```

3. **Access the application**:
   - React Dev Server: http://localhost:5173
   - Django API: http://localhost:8000/api/
   - Django Admin: http://localhost:8000/admin/

### Production Mode (with nginx)

1. **Build React frontend**:
   ```powershell
   cd frontend
   npm run build
   ```

2. **Copy build to nginx**:
   ```powershell
   Copy-Item -Path "dist\*" -Destination "C:\nginx\html\excel-verify" -Recurse -Force
   ```

3. **Start Django backend**:
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   python manage.py runserver 8000
   ```

4. **Start/Reload nginx**:
   ```powershell
   cd C:\nginx
   .\nginx.exe -s reload
   ```

5. **Access the application**:
   - Frontend: http://localhost
   - API (proxied): http://localhost/api/

## API Endpoints

- `POST /api/excel-uploads/upload/` - Upload Excel file
- `GET /api/excel-uploads/regex_patterns/` - Get available regex validation patterns
- `POST /api/excel-uploads/{id}/map_headers/` - Save header mappings and validation rules
- `POST /api/excel-uploads/{id}/validate/` - Validate data with user-selected rules
- `GET /api/excel-uploads/{id}/download/` - Download verified Excel
- `GET /api/mapping-templates/` - Get saved templates
- `POST /api/mapping-templates/save_template/` - Save new template

## Features

### Page 1: Upload & Header Mapping
- Drag-and-drop file upload
- Support for .xlsx, .xls, .csv files
- Automatic header extraction
- Data type inference
- Editable header mapping
- **Regex validation rule selection per column**:
  - **Mobile** - Phone number validation (various formats)
  - **Email** - Email address validation
  - **Alphanumeric** - Letters and numbers only
  - **Pincode** - 6-digit pincode validation
  - **None** - No validation
- Save/load mapping templates

### Page 2: Verification & Results
- Data validation with user-selected rules:
  - Mobile number format validation (if selected)
  - Email format validation (if selected)
  - Alphanumeric validation (if selected)
  - 6-digit pincode validation (if selected)
  - Required field checks (missing values)
  - Duplicate detection
- Visual validation report with statistics
- Data preview with mapped headers
- Download verified Excel with:
  - Mapped headers
  - Color-coded error/warning rows
  - Validation report sheet

## Troubleshooting

### Django Issues
- **Port 8000 in use**: Use `python manage.py runserver 8001`
- **CORS errors**: Check CORS_ALLOWED_ORIGINS in settings.py
- **File upload fails**: Check DATA_UPLOAD_MAX_MEMORY_SIZE in settings.py

### React Issues
- **Port 5173 in use**: Change port in vite.config.js
- **API calls fail**: Check proxy configuration in vite.config.js
- **Build fails**: Run `npm install` to ensure dependencies are installed

### nginx Issues
- **nginx won't start**: Check if port 80 is available
- **404 errors**: Verify build files are in C:\nginx\html\excel-verify
- **API proxy fails**: Ensure Django is running on port 8000
- **Test config**: Run `nginx -t` to check for syntax errors

## File Size Limits
- Current limit: 10MB
- To change: Update both `settings.py` (Django) and `nginx.conf` (nginx)

## Database
- **Current**: PostgreSQL (database: `excel_verification`)
- **See**: [DATABASE_SETUP.md](DATABASE_SETUP.md) for PostgreSQL configuration

## Security Notes (for Production)
1. Change SECRET_KEY in settings.py
2. Set DEBUG = False in settings.py
3. Configure proper ALLOWED_HOSTS
4. Use environment variables for sensitive data
5. Enable HTTPS in nginx
6. Add rate limiting
7. Configure proper CORS origins

## Maintenance

### Clear uploaded files
```powershell
Remove-Item -Path "backend\media\uploads\*" -Recurse -Force
```

### Reset database
```powershell
cd backend
Remove-Item -Path "db.sqlite3"
python manage.py migrate
```

### View logs
- Django: Console output
- nginx: C:\nginx\logs\error.log and access.log
