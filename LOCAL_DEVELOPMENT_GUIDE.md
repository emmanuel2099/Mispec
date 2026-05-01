# 🔧 Local Development Setup (No AWS Required)

## Problem Solved ✅

Your server couldn't start because it was trying to connect to AWS RDS PostgreSQL database, which requires internet connection. This guide sets up a **local SQLite database** so you can develop offline.

---

## 🚀 Quick Start (2 Steps)

### Step 1: Run the Local Server Script

**Windows:**
```bash
start_local_server.bat
```
Double-click the file OR run in terminal

**Linux/Mac:**
```bash
chmod +x start_local_server.sh
./start_local_server.sh
```

### Step 2: Create Admin Account

When prompted, create a superuser:
```
Username: admin
Email: admin@example.com
Password: (your password)
Password (again): (your password)
```

**That's it!** 🎉

---

## 🌐 Access Your Server

Once running, open your browser:

| Page | URL |
|------|-----|
| **Swagger UI** | `http://localhost:8000/` |
| **Admin Panel** | `http://localhost:8000/admin/` |
| **ReDoc** | `http://localhost:8000/redoc/` |

---

## 📊 What Changed?

### Before (Production Setup)
```
❌ Requires AWS RDS PostgreSQL
❌ Requires internet connection
❌ Requires Redis on AWS
❌ Complex setup
```

### After (Local Setup)
```
✅ Uses local SQLite database
✅ Works offline
✅ No Redis required
✅ Simple setup
```

---

## 🔍 Technical Details

### Files Created

1. **`mispec/settings_local.py`**
   - Overrides production settings
   - Uses SQLite instead of PostgreSQL
   - Disables Redis/Celery requirements

2. **`start_local_server.bat`** (Windows)
   - Automatically uses local settings
   - Creates database on first run
   - Prompts for superuser creation

3. **`start_local_server.sh`** (Linux/Mac)
   - Same as Windows version
   - Unix-compatible

### Database Location

Your local database is stored in:
```
mispec-backend/db.sqlite3
```

This file contains all your local data:
- Users
- Profiles
- Messages
- Events
- Everything!

---

## 🎯 Common Tasks

### Start Server
```bash
# Windows
start_local_server.bat

# Linux/Mac
./start_local_server.sh
```

### Create Superuser (if you skipped it)
```bash
python manage.py createsuperuser --settings=mispec.settings_local
```

### Run Migrations
```bash
python manage.py migrate --settings=mispec.settings_local
```

### Access Django Shell
```bash
python manage.py shell --settings=mispec.settings_local
```

### Run Tests
```bash
python test_all_apis.py
# Update BASE_URL in .env to http://localhost:8000
```

---

## 🔄 Switching Between Local and Production

### Use Local (Development)
```bash
# Windows
start_local_server.bat

# Linux/Mac
./start_local_server.sh

# Or manually
python manage.py runserver --settings=mispec.settings_local
```

### Use Production (AWS)
```bash
# Regular command (uses production settings)
python manage.py runserver
```

---

## 📝 Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Set Environment Variable
```bash
# Windows
set DJANGO_SETTINGS_MODULE=mispec.settings_local

# Linux/Mac
export DJANGO_SETTINGS_MODULE=mispec.settings_local
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Create Superuser
```bash
python manage.py createsuperuser
```

### 4. Start Server
```bash
python manage.py runserver
```

---

## 🐛 Troubleshooting

### Issue: "Module not found"
```bash
pip install -r requirements.txt
```

### Issue: "Database is locked"
- Close any other processes using the database
- Delete `db.sqlite3` and run migrations again

### Issue: "Port already in use"
```bash
# Use a different port
python manage.py runserver 8080 --settings=mispec.settings_local
```

### Issue: "Can't create superuser"
```bash
# Delete database and start fresh
del db.sqlite3  # Windows
rm db.sqlite3   # Linux/Mac

# Run migrations again
python manage.py migrate --settings=mispec.settings_local

# Create superuser
python manage.py createsuperuser --settings=mispec.settings_local
```

---

## 💡 Tips

### 1. Fresh Start
To start with a clean database:
```bash
# Delete the database
del db.sqlite3  # Windows
rm db.sqlite3   # Linux/Mac

# Run the local server script again
start_local_server.bat
```

### 2. Backup Your Data
```bash
# Backup
copy db.sqlite3 db.sqlite3.backup  # Windows
cp db.sqlite3 db.sqlite3.backup    # Linux/Mac

# Restore
copy db.sqlite3.backup db.sqlite3  # Windows
cp db.sqlite3.backup db.sqlite3    # Linux/Mac
```

### 3. View Database
Use a SQLite browser:
- **DB Browser for SQLite**: https://sqlitebrowser.org/
- Open `db.sqlite3` to view/edit data

---

## 🔐 Security Notes

### Local Development
- ✅ Safe to use DEBUG = True
- ✅ Safe to use simple passwords
- ✅ Safe to commit db.sqlite3 to git (if it's test data)

### Production
- ❌ Never use SQLite in production
- ❌ Never commit production database
- ❌ Always use strong passwords

---

## 📊 Comparison

| Feature | Local (SQLite) | Production (PostgreSQL) |
|---------|----------------|-------------------------|
| Setup | Easy | Complex |
| Internet | Not required | Required |
| Performance | Good for dev | Better for production |
| Concurrent users | Limited | Unlimited |
| Data size | Small to medium | Large |
| Cost | Free | AWS charges |

---

## 🎓 What You Can Do Now

With local setup, you can:

✅ **Develop offline** - No internet needed
✅ **Test APIs** - Use Swagger UI
✅ **Manage data** - Use Django Admin
✅ **Run tests** - Test all endpoints
✅ **Debug easily** - Local database is simple
✅ **Learn Django** - Experiment without risk

---

## 🚀 Next Steps

1. **Start the server**
   ```bash
   start_local_server.bat
   ```

2. **Access Swagger**
   ```
   http://localhost:8000/
   ```

3. **Login to Admin**
   ```
   http://localhost:8000/admin/
   ```

4. **Test APIs**
   - Register a user
   - Create profiles
   - Test messaging
   - Try all features!

---

## 📞 Need Help?

### Check These Files:
- `ACCESS_ADMIN_AND_SWAGGER.md` - How to use Admin & Swagger
- `VISUAL_GUIDE.md` - Visual walkthrough
- `QUICK_ACCESS_CARD.txt` - Quick reference

### Common Commands:
```bash
# Start local server
start_local_server.bat

# Create superuser
python manage.py createsuperuser --settings=mispec.settings_local

# Run migrations
python manage.py migrate --settings=mispec.settings_local

# Access shell
python manage.py shell --settings=mispec.settings_local
```

---

## ✅ Summary

**Problem:** Can't connect to AWS RDS database

**Solution:** Use local SQLite database

**How:** Run `start_local_server.bat`

**Result:** Server runs locally, no AWS needed!

---

**You're ready to develop! 🎉**

Just run `start_local_server.bat` and start coding!
