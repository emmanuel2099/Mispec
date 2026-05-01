# 🚀 START HERE - MISPEC API Testing

## What Was Created

I've created a **complete API testing suite** for your MISPEC backend with **55 endpoints** across 3 modules.

### 📦 Files Created (8 files)

| File | Purpose | Size |
|------|---------|------|
| `test_all_apis.py` | Main Python test script | 20 KB |
| `run_api_tests.bat` | Windows test runner | 2.4 KB |
| `run_api_tests.sh` | Linux/Mac test runner | 3.9 KB |
| `test_requirements.txt` | Python dependencies | 75 B |
| `MISPEC_API_Collection.postman_collection.json` | Postman collection | 20 KB |
| `API_TEST_README.md` | Detailed documentation | 5.1 KB |
| `API_ENDPOINTS_SUMMARY.md` | Endpoint reference | 7.9 KB |
| `TESTING_GUIDE.md` | Complete testing guide | 13 KB |

---

## ⚡ Quick Start (3 Steps)

### Step 1: Start Your Django Server
```bash
python manage.py runserver
```

### Step 2: Run Tests

**Windows:**
```bash
run_api_tests.bat
```

**Linux/Mac:**
```bash
chmod +x run_api_tests.sh
./run_api_tests.sh
```

**Or directly:**
```bash
pip install -r test_requirements.txt
python test_all_apis.py
```

### Step 3: View Results
- Check terminal for color-coded results
- ✅ Green = Pass
- ❌ Red = Fail  
- ⚠️ Yellow = Skipped

---

## 📊 What Gets Tested

### Users API (13 endpoints)
- ✅ OTP send/verify
- ✅ Registration & Login
- ✅ Token management
- ✅ Password reset
- ✅ Account deletion

### Profiles API (28 endpoints)
- ✅ Profile management
- ✅ Filtering & matching
- ✅ Likes & dislikes
- ✅ Blocking & reporting
- ✅ Gifts & referrals
- ✅ Notifications
- ✅ Support

### Chat API (14 endpoints)
- ✅ Messaging
- ✅ Voice/video calls
- ✅ Events management
- ✅ Chat rooms

**Total: 55 API endpoints tested!**

---

## 🎯 Three Ways to Test

### 1. Automated Python Script (Fastest)
```bash
python test_all_apis.py
```
- Tests all endpoints automatically
- Color-coded output
- Saves authentication tokens
- Best for: Quick comprehensive testing

### 2. Postman Collection (Most Visual)
1. Open Postman
2. Import `MISPEC_API_Collection.postman_collection.json`
3. Update `base_url` variable to `http://localhost:8000`
4. Run collection
- Best for: Manual testing & debugging

### 3. Swagger UI (Interactive)
1. Go to `http://localhost:8000/`
2. Try endpoints interactively
3. View documentation
- Best for: API exploration

---

## 🔧 Configuration

### Update Test Credentials

Edit `test_all_apis.py`:
```python
test_data = {
    'phone_number': '+1234567890',      # Your test phone
    'test_email': 'test@example.com',   # Your test email
    'test_password': 'TestPass123!',    # Your test password
}
```

### Update Base URL

Edit `.env`:
```env
BASE_URL=http://localhost:8000
```

Or for production:
```env
BASE_URL=https://your-production-url.com
```

---

## 📖 Documentation

### Quick Reference
- **`START_HERE.md`** ← You are here!
- **`TESTING_GUIDE.md`** - Complete testing guide with troubleshooting
- **`API_TEST_README.md`** - Detailed test documentation
- **`API_ENDPOINTS_SUMMARY.md`** - All 55 endpoints listed

### Interactive Docs
- Swagger UI: `http://localhost:8000/`
- ReDoc: `http://localhost:8000/redoc/`
- JSON Schema: `http://localhost:8000/api/api.json/`

---

## 🎬 Example Output

```
╔══════════════════════════════════════════════════════════════════════╗
║              MISPEC BACKEND API COMPREHENSIVE TEST SUITE             ║
║                   Base URL: http://localhost:8000                    ║
╚══════════════════════════════════════════════════════════════════════╝

================================================================================
                            USERS API TESTS
================================================================================

1. Testing OTP Flow
✓ PASS | POST   | /users/send_otp/                    | Status: 200 | OTP sent

2. Testing User Registration
✓ PASS | POST   | /users/register/                    | Status: 201 | User registered

3. Testing User Login
✓ PASS | POST   | /users/login/                       | Status: 200 | Login successful

================================================================================
                            PROFILES API TESTS
================================================================================

1. Testing Profile Update
✓ PASS | POST   | /profiles/profiles_update/          | Status: 200

2. Testing Profile Filter
✓ PASS | GET    | /profiles/profiles_filter/          | Status: 200

...

╔══════════════════════════════════════════════════════════════════════╗
║                        TEST SUITE COMPLETED                          ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## ❓ Common Issues

### Server Not Running
```bash
# Start Django server first
python manage.py runserver
```

### Dependencies Missing
```bash
# Install test dependencies
pip install -r test_requirements.txt
```

### Authentication Errors
```bash
# Update credentials in test_all_apis.py
# Or create a test user:
python manage.py createsuperuser
```

### Database Errors
```bash
# Run migrations
python manage.py migrate
```

---

## 🎯 Next Steps

1. **Run the tests** to see current API status
2. **Review failed tests** to identify issues
3. **Fix any bugs** found during testing
4. **Integrate with CI/CD** for automated testing
5. **Share with team** for collaborative testing

---

## 💡 Pro Tips

### Test Specific Module Only
Edit `test_all_apis.py` main function:
```python
def main():
    test_users_endpoints()      # Test only users
    # test_profiles_endpoints() # Comment out
    # test_chat_endpoints()     # Comment out
```

### Generate HTML Report
```bash
pytest test_all_apis.py --html=report.html
```

### Test Production
```bash
# Update .env with production URL
BASE_URL=https://your-production-url.com

# Run tests
python test_all_apis.py
```

### Use with Postman
1. Import collection
2. Set environment variables
3. Run entire collection
4. Export results

---

## 📞 Support

- **Email**: dev.team@mispec.co.uk
- **Docs**: See `TESTING_GUIDE.md` for detailed help
- **Logs**: Check Django server output for errors

---

## ✅ Checklist

Before running tests, ensure:

- [ ] Django server is running (`python manage.py runserver`)
- [ ] Database is migrated (`python manage.py migrate`)
- [ ] Dependencies installed (`pip install -r test_requirements.txt`)
- [ ] `.env` file configured with correct settings
- [ ] Test credentials updated in `test_all_apis.py`

---

## 🎉 Ready to Test!

You now have everything you need to test all 55 API endpoints!

**Choose your method:**
- 🚀 Quick automated test: `python test_all_apis.py`
- 🎯 Visual testing: Import Postman collection
- 📚 Interactive docs: Visit `http://localhost:8000/`

**Happy Testing! 🧪**

---

*For detailed instructions, see `TESTING_GUIDE.md`*
