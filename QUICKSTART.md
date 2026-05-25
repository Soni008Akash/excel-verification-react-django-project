# Excel Verify Project - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Setup (First Time Only)
Run the automated setup script:
```powershell
.\setup.ps1
```

This will:
- Create Python virtual environment
- Install all Python dependencies
- Run Django database migrations
- Install Node.js dependencies

### Step 2: Start Development Servers
Run the start script:
```powershell
.\start-dev.ps1
```

This opens two terminal windows:
- **Backend**: Django at http://localhost:8000
- **Frontend**: React at http://localhost:5173

### Step 3: Use the Application
1. Open browser: http://localhost:5173
2. Upload an Excel file (.xlsx, .xls, or .csv)
3. Map headers (rename columns as needed)
4. View validation results
5. Download verified Excel with report

---

## 📦 What's Included

### Backend (Django)
- ✅ REST API with 7 endpoints
- ✅ Excel file upload handling
- ✅ Header extraction & mapping
- ✅ **Flexible regex validation engine**:
  - **Mobile** number format
  - **Email** format
  - **Alphanumeric** validation
  - **6-digit pincode** validation
  - **No validation** option
  - Required field checks
  - Duplicate detection
- ✅ Verified Excel generation with color-coding

### Frontend (React)
- ✅ **Page 1: Upload & Mapping**
  - Drag-and-drop file upload
  - Automatic header extraction
  - Interactive header mapping
  - **Regex validation rule selection** (mobile, email, alphanumeric, pincode, none)
  - Save/load mapping templates
  
- ✅ **Page 2: Validation & Results**
  - Visual validation report
  - Data preview (50 rows)
  - Error/warning details
  - Download verified Excel

### Server (nginx)
- ✅ Configuration file included
- ✅ Deployment script ready
- ✅ Serves React frontend
- ✅ Proxies API requests to Django

---

## 🎯 Quick Test

1. **Start servers**: `.\start-dev.ps1`
2. **Open**: http://localhost:5173
3. **Create test CSV**: Create a file with this content:
   ```csv
   Name,Mobile,Email
   John Doe,1234567890,john@example.com
   Jane Smith,invalid,jane@example.com
   ```
4. **Upload** the file
5. **Map headers** (or keep as is)
6. **Click "Next: Verify Data"**
7. **View results** - should show 1 error (invalid phone on row 3)
8. **Download** verified Excel

---

## 🔧 Manual Setup (Alternative)

If you prefer manual setup:

### Backend
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

### Frontend
```powershell
cd frontend
npm install
npm run dev
```

---

## 🌐 Deploy to nginx (Production)

When ready for production:

```powershell
.\deploy.ps1
```

This will:
1. Build React for production
2. Copy files to nginx
3. Update nginx configuration
4. Reload nginx

Then start Django backend:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py runserver 8000
```

Access at: http://localhost

---

## 📚 Documentation

- **Regex Validation Guide**: REGEX_VALIDATION_GUIDE.md (NEW!)
- **Full Setup Guide**: README.md
- **Test Data**: TEST_DATA.md
- **API Endpoints**: See README.md
- **Project Plan**: /memories/session/plan.md

---

## ❓ Common Issues

**Q: Port 8000 already in use**
A: Change Django port: `python manage.py runserver 8001`
   Update vite.config.js proxy target

**Q: npm install fails**
A: Make sure Node.js 18+ is installed
   Try: `npm cache clean --force` then `npm install`

**Q: Python dependencies fail**
A: Make sure Python 3.8+ is installed
   Activate venv first: `.\venv\Scripts\Activate.ps1`

**Q: File upload fails**
A: Check backend/media/uploads folder exists
   Check Django settings.py MEDIA_ROOT

**Q: nginx deployment fails**
A: Verify nginx is at C:\nginx
   Update deploy.ps1 with correct path

---

## 🎉 Next Steps

1. **Test with sample data** (see TEST_DATA.md)
2. **Customize validation rules** (edit validators.py)
3. **Add more data types** (extend validation engine)
4. **Deploy to production** (run deploy.ps1)
5. **Add authentication** (if needed)

---

## 📞 Support

- Check README.md for detailed documentation
- Review TEST_DATA.md for testing examples
- Check browser console for frontend errors
- Check Django terminal for backend errors
- Review nginx logs: C:\nginx\logs\error.log

---

**Happy Excel Verifying! 📊✨**
