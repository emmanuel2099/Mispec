# 🌐 Testing Live/Production API

## 📍 What is Your Live API URL?

You mentioned the API is live. Please provide your production URL. Common formats:

### Heroku
```
https://your-app-name.herokuapp.com
```

### Custom Domain
```
https://api.mispec.co.uk
https://backend.mispec.co.uk
```

### AWS/Other Cloud
```
https://your-domain.com
```

---

## 🚀 Quick Setup to Test Live API

### Step 1: Update .env File

Open `.env` and update the `BASE_URL`:

```env
# Replace with your actual live API URL
BASE_URL = https://your-app-name.herokuapp.com
```

### Step 2: Run Tests Against Live API

```bash
python test_all_apis.py
```

This will test all 55 endpoints on your live server!

---

## 🔍 Find Your Live API URL

### If Deployed on Heroku:

1. **Check Heroku Dashboard**
   - Go to https://dashboard.heroku.com/
   - Find your app
   - URL will be: `https://your-app-name.herokuapp.com`

2. **Using Heroku CLI**
   ```bash
   heroku apps:info
   # Look for "Web URL"
   ```

### If Deployed on AWS/Other:

Check your deployment configuration or ask your DevOps team.

---

## 🌐 Access Live Swagger & Admin

Once you have the URL, you can access:

### Swagger UI (API Documentation)
```
https://your-live-url.com/
```

### Django Admin
```
https://your-live-url.com/admin/
```

### ReDoc
```
https://your-live-url.com/redoc/
```

---

## 🧪 Test Live API with Postman

### Step 1: Import Collection
1. Open Postman
2. Import `MISPEC_API_Collection.postman_collection.json`

### Step 2: Update Base URL
1. Click on the collection
2. Go to "Variables" tab
3. Update `base_url` to your live URL:
   ```
   https://your-live-url.com
   ```

### Step 3: Test Endpoints
1. Start with `/users/login/` to get a token
2. Use the token to test other endpoints

---

## 🔐 Testing with Live Data

### Important Notes:

⚠️ **Be Careful!**
- You're testing on **real production data**
- Don't delete important records
- Don't create spam data
- Use test accounts only

### Recommended Approach:

1. **Create Test User**
   ```json
   POST /users/register/
   {
     "email": "test@example.com",
     "password": "TestPass123!",
     "phone_number": "+1234567890"
   }
   ```

2. **Login with Test User**
   ```json
   POST /users/login/
   {
     "email": "test@example.com",
     "password": "TestPass123!"
   }
   ```

3. **Test Other Endpoints**
   - Use the test user for all operations
   - Don't interfere with real users

---

## 📊 Test Script Configuration

### Update test_all_apis.py

Open `test_all_apis.py` and update:

```python
# At the top of the file
BASE_URL = os.getenv('BASE_URL', 'https://your-live-url.com')

test_data = {
    'access_token': None,
    'refresh_token': None,
    'user_id': None,
    'phone_number': '+1234567890',  # Use a test phone
    'otp_code': None,
    'test_email': 'test@example.com',  # Use a test email
    'test_password': 'TestPass123!',
}
```

---

## 🎯 Common Live API URLs

Based on your project, your live API might be at:

### Option 1: Heroku
```
https://mispec-backend.herokuapp.com
https://mispec-api.herokuapp.com
https://mispec-dating.herokuapp.com
```

### Option 2: Custom Domain
```
https://api.mispec.co.uk
https://backend.mispec.co.uk
https://app.mispec.co.uk
```

### Option 3: AWS
```
https://mispec-api.us-east-1.elasticbeanstalk.com
```

---

## 🔧 Quick Test Commands

### Test if API is Live
```bash
curl https://your-live-url.com/
# Should return Swagger UI HTML
```

### Test Specific Endpoint
```bash
curl https://your-live-url.com/users/login/ \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}'
```

### Check API Health
```bash
curl https://your-live-url.com/admin/
# Should return admin login page
```

---

## 📝 Example: Complete Test Flow

### 1. Set Live URL
```bash
# In .env file
BASE_URL = https://mispec-backend.herokuapp.com
```

### 2. Test Registration
```bash
curl https://mispec-backend.herokuapp.com/users/register/ \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "phone_number": "+1234567890",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### 3. Test Login
```bash
curl https://mispec-backend.herokuapp.com/users/login/ \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

### 4. Run Full Test Suite
```bash
python test_all_apis.py
```

---

## 🌐 Access Live Admin Panel

### Step 1: Get Admin Credentials

You need a superuser account. If you don't have one:

**On Heroku:**
```bash
heroku run python manage.py createsuperuser --app your-app-name
```

**On AWS/Other:**
```bash
# SSH into your server
ssh your-server
cd /path/to/app
python manage.py createsuperuser
```

### Step 2: Login to Admin
```
https://your-live-url.com/admin/
```

---

## 📊 What You Can Do with Live API

### View Live Data
- See real users
- Check actual profiles
- View real messages
- Monitor events

### Test Features
- Test authentication flow
- Test profile matching
- Test messaging
- Test video calls

### Monitor Performance
- Check response times
- Monitor error rates
- View API usage

---

## ⚠️ Safety Guidelines

### DO:
✅ Use test accounts
✅ Test in off-peak hours
✅ Document your tests
✅ Clean up test data
✅ Monitor for errors

### DON'T:
❌ Delete real user data
❌ Spam the API
❌ Test payment features with real money
❌ Share admin credentials
❌ Commit credentials to git

---

## 🔍 Troubleshooting Live API

### Issue: Can't Connect
```bash
# Check if API is up
curl https://your-live-url.com/
```

### Issue: 401 Unauthorized
- Check if token is valid
- Login again to get new token
- Verify token format: `Bearer <token>`

### Issue: 500 Server Error
- Check server logs
- Contact DevOps team
- Check database connection

### Issue: Slow Response
- API might be under load
- Check server resources
- Consider caching

---

## 📞 Need Your Live URL?

**Please provide your live API URL so I can:**
1. Update the test scripts
2. Configure Postman collection
3. Create specific test cases
4. Help you access Swagger/Admin

**Common places to find it:**
- Heroku dashboard
- AWS console
- Domain registrar
- Deployment logs
- Ask your team

---

## 🎯 Next Steps

1. **Find your live URL**
   - Check Heroku/AWS dashboard
   - Ask your DevOps team

2. **Update .env file**
   ```env
   BASE_URL = https://your-actual-live-url.com
   ```

3. **Test the API**
   ```bash
   python test_all_apis.py
   ```

4. **Access Swagger**
   ```
   https://your-live-url.com/
   ```

---

## 💡 Quick Reference

| What | Where |
|------|-------|
| **Live Swagger** | `https://your-live-url.com/` |
| **Live Admin** | `https://your-live-url.com/admin/` |
| **Test Script** | `python test_all_apis.py` |
| **Postman** | Import collection, update base_url |

---

**Please share your live API URL and I'll help you test it! 🚀**
