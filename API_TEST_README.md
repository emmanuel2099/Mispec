# MISPEC Backend API Testing Guide

## Overview
This comprehensive test suite tests all backend API endpoints across three main modules:
- **Users** (13 endpoints) - Authentication, registration, password management
- **Profiles** (28 endpoints) - Profile management, matching, gifts, notifications
- **Chat** (14 endpoints) - Messaging, calls, events

**Total: 55 API endpoints**

## Setup Instructions

### 1. Install Test Dependencies
```bash
pip install -r test_requirements.txt
```

### 2. Configure Environment
Update your `.env` file or create a new one with:
```env
BASE_URL=http://localhost:8000
# Or use your deployed URL:
# BASE_URL=https://your-backend.herokuapp.com
```

### 3. Update Test Data
Edit `test_all_apis.py` and update the `test_data` dictionary:
```python
test_data = {
    'phone_number': '+1234567890',  # Your test phone number
    'test_email': 'test@example.com',  # Your test email
    'test_password': 'TestPass123!',  # Your test password
}
```

## Running Tests

### Run All Tests
```bash
python test_all_apis.py
```

### Run with Server
Make sure your Django server is running:
```bash
# Terminal 1: Start Django server
python manage.py runserver

# Terminal 2: Run tests
python test_all_apis.py
```

## Test Coverage

### Users API (`/users/`)
✓ Send OTP
✓ Verify OTP
✓ Register User
✓ Login
✓ Token Refresh
✓ Provider Auth (Social Login)
✓ Create Referral
✓ Change Password
✓ Reset Password Request
✓ Reset Password Verify
✓ Logout
✓ Delete Account

### Profiles API (`/profiles/`)
✓ Profile Update
✓ Profile Filter
✓ Both Profile Filter
✓ Entertainment
✓ Sport
✓ Media Delete
✓ Like Create
✓ Liked Profiles
✓ Report Create
✓ Reported Profiles
✓ Block Create
✓ Blocked Profiles
✓ Matches
✓ Profile Gift
✓ Owned Gift
✓ Received Gift
✓ Profile Unblock
✓ Referrals
✓ Redeem Gift
✓ Redeem Referral
✓ Dislike
✓ Chat Notifications
✓ Notifications
✓ Read Notification
✓ Send Gift
✓ Gifts List
✓ Verify Purchase
✓ Support

### Chat API (`/chat/`)
✓ Messages
✓ Active Chatrooms
✓ Make Call
✓ Join Call
✓ Call History
✓ Create Room
✓ Create Event
✓ Edit Event
✓ Event Detail
✓ Add Member
✓ Stop Event
✓ Leave Event
✓ Report Event
✓ End Call

## Test Output

The script provides color-coded output:
- 🟢 **GREEN** = Test passed
- 🔴 **RED** = Test failed
- 🟡 **YELLOW** = Test skipped (requires specific data)

Example output:
```
================================================================================
                            USERS API TESTS
================================================================================

1. Testing OTP Flow
✓ PASS | POST   | /users/send_otp/                                  | Status: 200 | OTP sent

2. Testing User Registration
✓ PASS | POST   | /users/register/                                  | Status: 201 | User registered

3. Testing User Login
✓ PASS | POST   | /users/login/                                     | Status: 200 | Login successful, token saved
```

## Notes

### Skipped Tests
Some tests are skipped by default because they:
1. Require manual input (OTP codes)
2. Need specific IDs (profile_id, event_id, etc.)
3. Are destructive operations (delete account)
4. Require external OAuth tokens

### Authentication Flow
The script automatically:
1. Registers a test user (if needed)
2. Logs in and stores the access token
3. Uses the token for authenticated endpoints
4. Tests token refresh

### Customization
To test specific endpoints with real data:
1. Update the test data in the respective test function
2. Remove the "Skipped" logic for that endpoint
3. Provide required IDs or parameters

## Troubleshooting

### Connection Errors
- Ensure Django server is running
- Check BASE_URL in .env file
- Verify firewall/network settings

### Authentication Errors
- Check if user exists in database
- Verify credentials in test_data
- Ensure JWT tokens are valid

### Database Errors
- Run migrations: `python manage.py migrate`
- Check database connection in .env
- Verify PostgreSQL is running

## Advanced Usage

### Testing Against Production
```bash
# Update .env
BASE_URL=https://your-production-url.com

# Run tests
python test_all_apis.py
```

### Integration with CI/CD
Add to your `bitbucket-pipelines.yml`:
```yaml
- step:
    name: API Tests
    script:
      - pip install -r test_requirements.txt
      - python test_all_apis.py
```

### Generate HTML Report
```bash
pytest test_all_apis.py --html=report.html --self-contained-html
```

## API Documentation
Access the interactive API documentation:
- Swagger UI: `http://localhost:8000/`
- ReDoc: `http://localhost:8000/redoc/`
- JSON Schema: `http://localhost:8000/api/api.json/`

## Support
For issues or questions:
- Email: dev.team@mispec.co.uk
- Check Django logs: `python manage.py runserver` output
- Review test output for specific error messages
