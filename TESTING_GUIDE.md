# 🧪 Complete API Testing Guide for MISPEC Backend

## 📋 Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Testing Methods](#testing-methods)
4. [Detailed Instructions](#detailed-instructions)
5. [Troubleshooting](#troubleshooting)

---

## Overview

This guide provides **3 different ways** to test all 55 API endpoints in your MISPEC backend:

### ✅ What's Been Created for You

1. **`test_all_apis.py`** - Automated Python test script
2. **`MISPEC_API_Collection.postman_collection.json`** - Postman collection
3. **`run_api_tests.sh`** - Linux/Mac test runner
4. **`run_api_tests.bat`** - Windows test runner
5. **`API_TEST_README.md`** - Detailed documentation
6. **`API_ENDPOINTS_SUMMARY.md`** - Complete endpoint reference
7. **`test_requirements.txt`** - Python dependencies

---

## Quick Start

### Option 1: Automated Testing (Recommended)

**Windows:**
```bash
# Double-click run_api_tests.bat
# OR run in terminal:
run_api_tests.bat
```

**Linux/Mac:**
```bash
chmod +x run_api_tests.sh
./run_api_tests.sh
```

### Option 2: Manual Python Script
```bash
# Install dependencies
pip install -r test_requirements.txt

# Run tests
python test_all_apis.py
```

### Option 3: Postman (GUI Testing)
1. Open Postman
2. Import `MISPEC_API_Collection.postman_collection.json`
3. Update `base_url` variable
4. Run collection

---

## Testing Methods

### Method 1: Automated Python Script ⚡

**Best for**: Quick comprehensive testing, CI/CD integration

**Steps:**
1. Ensure Django server is running:
   ```bash
   python manage.py runserver
   ```

2. Run the test script:
   ```bash
   python test_all_apis.py
   ```

**Features:**
- ✅ Tests all 55 endpoints automatically
- ✅ Color-coded output (Pass/Fail/Skip)
- ✅ Automatic token management
- ✅ Detailed error messages
- ✅ Progress tracking

**Sample Output:**
```
================================================================================
                            USERS API TESTS
================================================================================

1. Testing OTP Flow
✓ PASS | POST   | /users/send_otp/                    | Status: 200 | OTP sent

2. Testing User Registration
✓ PASS | POST   | /users/register/                    | Status: 201 | User registered

3. Testing User Login
✓ PASS | POST   | /users/login/                       | Status: 200 | Login successful
```

---

### Method 2: Postman Collection 🎯

**Best for**: Manual testing, debugging, API exploration

**Steps:**

1. **Install Postman**
   - Download from: https://www.postman.com/downloads/

2. **Import Collection**
   - Open Postman
   - Click "Import" button
   - Select `MISPEC_API_Collection.postman_collection.json`
   - Click "Import"

3. **Configure Variables**
   - Click on collection name
   - Go to "Variables" tab
   - Update `base_url` (e.g., `http://localhost:8000`)
   - Save

4. **Test Authentication Flow**
   - Open "Users API" folder
   - Run "Register" request
   - Run "Login" request (saves token automatically)
   - Other requests will use the saved token

5. **Run All Tests**
   - Click on collection name
   - Click "Run" button
   - Select all requests
   - Click "Run MISPEC Backend API"

**Features:**
- ✅ Visual interface
- ✅ Request/response inspection
- ✅ Automatic token management
- ✅ Save test data
- ✅ Environment variables
- ✅ Test scripts

---

### Method 3: Swagger UI 📚

**Best for**: Interactive documentation, quick endpoint testing

**Steps:**

1. **Start Django Server**
   ```bash
   python manage.py runserver
   ```

2. **Open Swagger UI**
   - Navigate to: `http://localhost:8000/`
   - You'll see interactive API documentation

3. **Authenticate**
   - Scroll to "Users" section
   - Try "POST /users/login/" endpoint
   - Click "Try it out"
   - Enter credentials
   - Click "Execute"
   - Copy the `access` token from response

4. **Authorize**
   - Click "Authorize" button at top
   - Enter: `Bearer <your_access_token>`
   - Click "Authorize"

5. **Test Endpoints**
   - Navigate to any endpoint
   - Click "Try it out"
   - Fill in parameters
   - Click "Execute"
   - View response

**Features:**
- ✅ Built-in documentation
- ✅ No setup required
- ✅ Real-time testing
- ✅ Request/response examples
- ✅ Schema validation

---

## Detailed Instructions

### Prerequisites

1. **Python 3.7+** installed
2. **Django server** running
3. **Database** configured and migrated
4. **Environment variables** set in `.env`

### Step-by-Step: First Time Setup

#### 1. Verify Django Server
```bash
# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start server
python manage.py runserver
```

Verify server is running by visiting: `http://localhost:8000/`

#### 2. Install Test Dependencies
```bash
pip install -r test_requirements.txt
```

This installs:
- `requests` - HTTP library
- `python-dotenv` - Environment variable management
- `pytest` - Testing framework
- `pytest-html` - HTML report generation

#### 3. Configure Test Data

Edit `test_all_apis.py` and update:

```python
test_data = {
    'phone_number': '+1234567890',      # Valid phone number
    'test_email': 'test@example.com',   # Test email
    'test_password': 'TestPass123!',    # Test password
}
```

#### 4. Run Tests

**Option A: Using Runner Script**
```bash
# Windows
run_api_tests.bat

# Linux/Mac
./run_api_tests.sh
```

**Option B: Direct Python**
```bash
python test_all_apis.py
```

#### 5. Review Results

The script will output:
- ✅ **Green** = Test passed
- ❌ **Red** = Test failed
- ⚠️ **Yellow** = Test skipped

---

### Understanding Test Results

#### Successful Test
```
✓ PASS | POST   | /users/login/     | Status: 200 | Login successful, token saved
```
- Endpoint responded correctly
- Status code is 200 (or expected code)
- Response contains expected data

#### Failed Test
```
✗ FAIL | POST   | /users/login/     | Status: 401 | Invalid credentials
```
- Endpoint returned error
- Check credentials or data
- Review error message

#### Skipped Test
```
⚠ SKIP | POST   | /users/verify_otp/ | Status: 0   | Skipped - requires manual OTP
```
- Test requires manual input
- Or needs specific data (IDs, tokens)
- Or is destructive operation

---

### Testing Specific Modules

#### Test Only Users API
Edit `test_all_apis.py` and comment out:
```python
def main():
    test_users_endpoints()
    # test_profiles_endpoints()  # Comment out
    # test_chat_endpoints()       # Comment out
```

#### Test Only Profiles API
```python
def main():
    # test_users_endpoints()      # Comment out
    test_profiles_endpoints()
    # test_chat_endpoints()       # Comment out
```

#### Test Only Chat API
```python
def main():
    # test_users_endpoints()      # Comment out
    # test_profiles_endpoints()   # Comment out
    test_chat_endpoints()
```

---

## Troubleshooting

### Issue: Connection Error

**Error:**
```
✗ FAIL | POST   | /users/login/     | Status: 0   | Connection error
```

**Solutions:**
1. Check if Django server is running:
   ```bash
   python manage.py runserver
   ```

2. Verify BASE_URL in `.env`:
   ```env
   BASE_URL=http://localhost:8000
   ```

3. Check firewall settings

4. Try accessing in browser: `http://localhost:8000/`

---

### Issue: Authentication Failed

**Error:**
```
✗ FAIL | POST   | /users/login/     | Status: 401 | Invalid credentials
```

**Solutions:**
1. Verify user exists in database:
   ```bash
   python manage.py shell
   >>> from django.contrib.auth import get_user_model
   >>> User = get_user_model()
   >>> User.objects.filter(email='test@example.com').exists()
   ```

2. Create test user:
   ```bash
   python manage.py createsuperuser
   ```

3. Update credentials in `test_all_apis.py`

4. Check password requirements

---

### Issue: Database Error

**Error:**
```
✗ FAIL | POST   | /users/register/  | Status: 500 | Database error
```

**Solutions:**
1. Run migrations:
   ```bash
   python manage.py migrate
   ```

2. Check database connection in `.env`:
   ```env
   DATABASE_URL=postgres://...
   ```

3. Verify PostgreSQL is running

4. Check Django logs for details

---

### Issue: Missing Dependencies

**Error:**
```
ModuleNotFoundError: No module named 'requests'
```

**Solutions:**
1. Install dependencies:
   ```bash
   pip install -r test_requirements.txt
   ```

2. Activate virtual environment:
   ```bash
   # Windows
   .venv\Scripts\activate

   # Linux/Mac
   source .venv/bin/activate
   ```

3. Verify installation:
   ```bash
   pip list
   ```

---

### Issue: OTP Tests Failing

**Error:**
```
✗ FAIL | POST   | /users/verify_otp/ | Status: 400 | Invalid OTP
```

**Solutions:**
1. OTP tests require manual intervention
2. Run send_otp endpoint first
3. Check your phone/email for OTP
4. Update test script with actual OTP
5. Or skip OTP tests (they're marked as skipped by default)

---

### Issue: Token Expired

**Error:**
```
✗ FAIL | GET    | /profiles/matches/ | Status: 401 | Token expired
```

**Solutions:**
1. Re-run login test to get fresh token
2. Check token expiration settings in Django
3. Use token refresh endpoint
4. The script handles this automatically

---

## Advanced Testing

### Generate HTML Report

```bash
pytest test_all_apis.py --html=report.html --self-contained-html
```

Open `report.html` in browser to view detailed results.

---

### Test Against Production

1. Update `.env`:
   ```env
   BASE_URL=https://your-production-url.com
   ```

2. Use production credentials

3. Run tests:
   ```bash
   python test_all_apis.py
   ```

⚠️ **Warning**: Be careful with destructive operations (delete, block, etc.)

---

### CI/CD Integration

Add to `bitbucket-pipelines.yml`:

```yaml
pipelines:
  default:
    - step:
        name: Run API Tests
        script:
          - pip install -r test_requirements.txt
          - python test_all_apis.py
        services:
          - postgres
```

---

### Custom Test Scenarios

Create your own test file:

```python
from test_all_apis import test_endpoint, get_headers, test_data

# Login first
success, status, data = test_endpoint(
    'POST', '/users/login/',
    {'email': 'user@example.com', 'password': 'pass123'}
)
test_data['access_token'] = data['access']

# Test custom scenario
success, status, data = test_endpoint(
    'GET', '/profiles/matches/',
    auth=True
)
print(f"Found {len(data)} matches")
```

---

## Best Practices

### 1. Test Order
- Always test authentication first
- Then test profile operations
- Finally test chat/messaging

### 2. Data Cleanup
- Use test database
- Clean up after tests
- Don't use production data

### 3. Error Handling
- Check status codes
- Validate response structure
- Log errors for debugging

### 4. Security
- Don't commit credentials
- Use environment variables
- Rotate test tokens regularly

### 5. Documentation
- Document test scenarios
- Keep README updated
- Share results with team

---

## Quick Reference

### All 55 Endpoints

**Users (13)**
- send_otp, verify_otp, register, login, logout
- token, token/refresh, auth_provider
- create_referral, change_password
- reset_password_request, reset_password_verify
- delete_account

**Profiles (28)**
- profiles_update, profiles_filter, both_profiles_filter
- entertainment, sport, media_delete
- like_create, liked_profiles, dislike, matches
- report_create, reported_profiles
- block_create, blocked_profiles, profile_unblock
- profile_gift, owned_gift, received_gift, redeem_gift
- referrals, redeem_referral
- chat_notifications, notifications, read_notification
- send_gift, gifts, verify_purchase, support

**Chat (14)**
- messages, active_chatrooms, create_room
- make_call, join_call, end_call, call_history
- create_event, edit_event, event_detail
- add_member, leave_event, stop_event, report_event

---

## Support & Resources

### Documentation
- `API_TEST_README.md` - Detailed testing guide
- `API_ENDPOINTS_SUMMARY.md` - Complete endpoint reference
- Swagger UI: `http://localhost:8000/`
- ReDoc: `http://localhost:8000/redoc/`

### Contact
- Email: dev.team@mispec.co.uk
- Check Django logs for errors
- Review test output for details

### Useful Commands
```bash
# Start server
python manage.py runserver

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python test_all_apis.py

# Check logs
python manage.py runserver --verbosity 3
```

---

**Happy Testing! 🚀**
