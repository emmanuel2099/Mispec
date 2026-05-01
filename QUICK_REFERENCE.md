# ⚡ Quick Reference - MISPEC API Testing

## 🎯 What You Need to Know

### ✅ What Was Created
- **10 files** for comprehensive API testing
- Tests for **55 endpoints** across 3 modules
- **4 different ways** to test your APIs
- Complete documentation and guides

---

## 🚀 How to Run Tests (Pick One)

### Option 1: Fastest Way (Windows)
```bash
run_api_tests.bat
```

### Option 2: Fastest Way (Linux/Mac)
```bash
chmod +x run_api_tests.sh
./run_api_tests.sh
```

### Option 3: Direct Python
```bash
pip install -r test_requirements.txt
python test_all_apis.py
```

### Option 4: Postman (Visual)
1. Open Postman
2. Import `MISPEC_API_Collection.postman_collection.json`
3. Set `base_url` to `http://localhost:8000`
4. Click "Run Collection"

---

## 📋 Prerequisites Checklist

Before running tests:
- [ ] Django server running: `python manage.py runserver`
- [ ] Database migrated: `python manage.py migrate`
- [ ] `.env` file configured
- [ ] Test credentials updated in `test_all_apis.py`

---

## 📚 Documentation Files

| File | When to Read |
|------|--------------|
| **START_HERE.md** | First time setup |
| **QUICK_REFERENCE.md** | Quick commands (this file) |
| **TESTING_GUIDE.md** | Detailed guide + troubleshooting |
| **API_TEST_README.md** | Test documentation |
| **API_ENDPOINTS_SUMMARY.md** | All 55 endpoints |
| **TEST_STRUCTURE.txt** | Visual structure |

---

## 🎨 Understanding Test Output

```
✓ PASS | POST   | /users/login/     | Status: 200 | Success
```
- ✅ **Green** = Test passed successfully

```
✗ FAIL | POST   | /users/login/     | Status: 401 | Invalid credentials
```
- ❌ **Red** = Test failed, needs attention

```
⚠ SKIP | POST   | /users/verify_otp/ | Status: 0   | Requires manual OTP
```
- ⚠️ **Yellow** = Test skipped (requires manual input or specific data)

---

## 🔧 Common Commands

### Start Django Server
```bash
python manage.py runserver
```

### Run Migrations
```bash
python manage.py migrate
```

### Create Test User
```bash
python manage.py createsuperuser
```

### Install Test Dependencies
```bash
pip install -r test_requirements.txt
```

### Run All Tests
```bash
python test_all_apis.py
```

### View API Documentation
```bash
# Start server, then visit:
http://localhost:8000/          # Swagger UI
http://localhost:8000/redoc/    # ReDoc
```

---

## 📊 API Modules

### Users (13 endpoints)
Authentication, registration, password management

### Profiles (28 endpoints)
Profile management, matching, gifts, notifications

### Chat (14 endpoints)
Messaging, calls, events

**Total: 55 endpoints**

---

## 🐛 Quick Troubleshooting

### Server Not Running
```bash
python manage.py runserver
```

### Connection Error
Check `.env` file:
```env
BASE_URL=http://localhost:8000
```

### Authentication Failed
Update credentials in `test_all_apis.py`:
```python
test_data = {
    'test_email': 'your@email.com',
    'test_password': 'YourPassword123!',
}
```

### Module Not Found
```bash
pip install -r test_requirements.txt
```

### Database Error
```bash
python manage.py migrate
```

---

## 💡 Pro Tips

### Test Specific Module
Edit `test_all_apis.py`:
```python
def main():
    test_users_endpoints()      # Only test users
    # test_profiles_endpoints() # Comment out
    # test_chat_endpoints()     # Comment out
```

### Test Production
Update `.env`:
```env
BASE_URL=https://your-production-url.com
```

### Generate HTML Report
```bash
pytest test_all_apis.py --html=report.html
```

---

## 🎯 Test Flow

1. **Authentication** → Login and get token
2. **Token Storage** → Automatically saved
3. **Authenticated Requests** → Use saved token
4. **Token Refresh** → Automatic when expired

---

## 📞 Need Help?

1. **Read**: `TESTING_GUIDE.md` for detailed help
2. **Check**: Django server logs for errors
3. **Email**: dev.team@mispec.co.uk

---

## ⚡ One-Liner Commands

```bash
# Complete test run (Windows)
run_api_tests.bat

# Complete test run (Linux/Mac)
./run_api_tests.sh

# Quick test
python test_all_apis.py

# Start server
python manage.py runserver

# View docs
start http://localhost:8000/
```

---

## 🎉 You're Ready!

Everything is set up. Just run:
```bash
python test_all_apis.py
```

**Happy Testing! 🚀**

---

*For detailed instructions, see `START_HERE.md` or `TESTING_GUIDE.md`*
