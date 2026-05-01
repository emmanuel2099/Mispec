# 📸 Visual Guide - Admin & Swagger Access

## 🚀 Step-by-Step Visual Guide

---

## Step 1: Start the Server

### Option A: Double-click the script
```
📁 mispec-backend/
  └── start_server.bat  ← Double-click this file
```

### Option B: Run manually
```bash
python manage.py runserver
```

### You'll see:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
December 31, 2024 - 10:00:00
Django version 5.0.2, using settings 'mispec.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

✅ **Server is running!**

---

## Step 2: Access Swagger UI

### Open your browser and go to:
```
http://localhost:8000/
```

### What You'll See:

```
┌─────────────────────────────────────────────────────────────────┐
│  MISPEC API                                          [Authorize] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Test description                                                │
│  Version: v1                                                     │
│                                                                  │
│  ▼ users - User authentication and management                   │
│     ┌──────────────────────────────────────────────────────┐   │
│     │ POST /users/send_otp/          Send OTP              │   │
│     │ POST /users/verify_otp/        Verify OTP            │   │
│     │ POST /users/register/          Register user         │   │
│     │ POST /users/login/             Login                 │   │
│     │ POST /users/logout/            Logout                │   │
│     │ POST /users/api/token/         Get JWT token         │   │
│     │ POST /users/api/token/refresh/ Refresh token         │   │
│     │ POST /users/auth_provider/     Social login          │   │
│     │ POST /users/create_referral/   Create referral       │   │
│     │ POST /users/change_password/   Change password       │   │
│     │ POST /users/reset_password_request/                  │   │
│     │ POST /users/reset_password_verify/                   │   │
│     │ DELETE /users/delete_account/  Delete account        │   │
│     └──────────────────────────────────────────────────────┘   │
│                                                                  │
│  ▼ profiles - Profile management                                │
│     ┌──────────────────────────────────────────────────────┐   │
│     │ POST /profiles/profiles_update/                      │   │
│     │ GET  /profiles/profiles_filter/                      │   │
│     │ GET  /profiles/both_profiles_filter/                 │   │
│     │ GET  /profiles/entertainment/                        │   │
│     │ GET  /profiles/sport/                                │   │
│     │ DELETE /profiles/media_delete/                       │   │
│     │ POST /profiles/like_create/                          │   │
│     │ GET  /profiles/liked_profiles/                       │   │
│     │ ... (20 more endpoints)                              │   │
│     └──────────────────────────────────────────────────────┘   │
│                                                                  │
│  ▼ chat - Messaging and calls                                   │
│     ┌──────────────────────────────────────────────────────┐   │
│     │ GET  /chat/messages/                                 │   │
│     │ GET  /chat/active_chatrooms/                         │   │
│     │ POST /chat/make_call/                                │   │
│     │ POST /chat/join_call/                                │   │
│     │ GET  /chat/call_history/                             │   │
│     │ POST /chat/create_room/                              │   │
│     │ POST /chat/create_event/                             │   │
│     │ ... (7 more endpoints)                               │   │
│     └──────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 3: Test an Endpoint in Swagger

### Example: Testing Login

1. **Click on** `POST /users/login/`

```
┌─────────────────────────────────────────────────────────────────┐
│  POST /users/login/                                    [Expand] │
├─────────────────────────────────────────────────────────────────┤
│  Login with email and password                                  │
│                                                                  │
│  [Try it out]                                                   │
└─────────────────────────────────────────────────────────────────┘
```

2. **Click** `Try it out`

3. **Fill in the request body:**

```json
{
  "email": "test@example.com",
  "password": "TestPass123!"
}
```

4. **Click** `Execute`

5. **See the response:**

```
Response Code: 200

Response Body:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User"
  }
}
```

---

## Step 4: Authorize in Swagger

### After getting the access token:

1. **Copy the access token** from the login response

2. **Click the** `Authorize` **button** at the top right

```
┌─────────────────────────────────────────────────────────────────┐
│  Available authorizations                                        │
├─────────────────────────────────────────────────────────────────┤
│  Bearer (http, Bearer)                                           │
│                                                                  │
│  Value: [Bearer eyJ0eXAiOiJKV1QiLCJhbGc...]                     │
│                                                                  │
│  [Authorize]  [Close]                                           │
└─────────────────────────────────────────────────────────────────┘
```

3. **Enter:** `Bearer <your_access_token>`

4. **Click** `Authorize`

5. **Now you can test authenticated endpoints!** 🎉

---

## Step 5: Access Django Admin

### Open your browser and go to:
```
http://localhost:8000/admin/
```

### Login Screen:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│                    Django administration                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Username: [________________]                          │    │
│  │  Password: [________________]                          │    │
│  │                                                         │    │
│  │  [Log in]                                              │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### After Login - Admin Dashboard:

```
┌─────────────────────────────────────────────────────────────────┐
│  Django administration                    Welcome, admin [Logout]│
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Site administration                                             │
│                                                                  │
│  ┌─ AUTHENTICATION AND AUTHORIZATION ─────────────────────┐    │
│  │  👥 Users                                    [+ Add]    │    │
│  │  👥 Groups                                   [+ Add]    │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─ USERS ─────────────────────────────────────────────────┐    │
│  │  👤 Custom users                             [+ Add]    │    │
│  │  📱 Otp checks                               [+ Add]    │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─ PROFILES ──────────────────────────────────────────────┐    │
│  │  👤 Profiles                                 [+ Add]    │    │
│  │  📸 Profile medias                           [+ Add]    │    │
│  │  ❤️  Likes                                    [+ Add]    │    │
│  │  💑 Matches                                  [+ Add]    │    │
│  │  🚫 Blocks                                   [+ Add]    │    │
│  │  ⚠️  Reports                                  [+ Add]    │    │
│  │  🎁 Gifts                                    [+ Add]    │    │
│  │  🔔 Notifications                            [+ Add]    │    │
│  │  🎭 Entertainment                            [+ Add]    │    │
│  │  ⚽ Sport                                     [+ Add]    │    │
│  │  💎 Plans                                    [+ Add]    │    │
│  │  📋 User plans                               [+ Add]    │    │
│  │  🔗 Referrals                                [+ Add]    │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─ CHAT ──────────────────────────────────────────────────┐    │
│  │  💬 Chat rooms                               [+ Add]    │    │
│  │  📨 Messages                                 [+ Add]    │    │
│  │  👥 Memberships                              [+ Add]    │    │
│  │  🎉 Events                                   [+ Add]    │    │
│  │  📞 Call rooms                               [+ Add]    │    │
│  │  ⏱️  Call durations                          [+ Add]    │    │
│  │  💌 Message allowances                       [+ Add]    │    │
│  │  ⚠️  Event reports                           [+ Add]    │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Recent actions                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  None available                                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 6: Manage Data in Admin

### Example: View Users

1. **Click on** `Custom users`

```
┌─────────────────────────────────────────────────────────────────┐
│  Select custom user to change                                    │
├─────────────────────────────────────────────────────────────────┤
│  [+ Add custom user]                                             │
│                                                                  │
│  Search: [_____________] [Go]                                   │
│                                                                  │
│  Filter:                                                         │
│  By date joined                                                  │
│  □ Today                                                         │
│  □ Past 7 days                                                   │
│  □ This month                                                    │
│  □ This year                                                     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ ☑ Email              First Name  Last Name  Active     │     │
│  ├────────────────────────────────────────────────────────┤     │
│  │ □ test@example.com   Test        User       ✓         │     │
│  │ □ user2@example.com  John        Doe        ✓         │     │
│  │ □ user3@example.com  Jane        Smith      ✓         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  3 custom users                                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

2. **Click on a user** to edit

```
┌─────────────────────────────────────────────────────────────────┐
│  Change custom user                                              │
├─────────────────────────────────────────────────────────────────┤
│  Email address: [test@example.com_______________]               │
│  First name:    [Test________________________]                  │
│  Last name:     [User________________________]                  │
│  Phone number:  [+1234567890_________________]                  │
│  Is active:     ☑                                               │
│  Is staff:      □                                               │
│  Is superuser:  □                                               │
│  Date joined:   2024-12-31 10:00:00                             │
│  Last login:    2024-12-31 11:30:00                             │
│                                                                  │
│  [Save and continue editing]  [Save]  [Delete]                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 What You Can Do

### In Swagger UI:
✅ Test all 55 API endpoints
✅ View request/response formats
✅ Try authentication flow
✅ Test with real data
✅ Download API schema
✅ Share with team

### In Django Admin:
✅ View all users
✅ Manage profiles
✅ View matches and likes
✅ Check chat messages
✅ Monitor events
✅ View call history
✅ Manage gifts and referrals
✅ Check notifications
✅ Handle reports and blocks
✅ Manage subscriptions

---

## 🎯 Quick Tips

### Swagger UI Tips:
1. **Use "Try it out"** to test endpoints interactively
2. **Authorize first** before testing protected endpoints
3. **Check "Responses"** tab to see possible status codes
4. **Use "Models"** section to understand data structures
5. **Download schema** for Postman import

### Admin Panel Tips:
1. **Use search** to find specific records quickly
2. **Use filters** on the right sidebar
3. **Bulk actions** for multiple records
4. **Click column headers** to sort
5. **Use "History"** to see changes
6. **Export data** using admin actions

---

## 🔗 All Access URLs

| What | URL | When to Use |
|------|-----|-------------|
| **Swagger UI** | `http://localhost:8000/` | Test APIs interactively |
| **ReDoc** | `http://localhost:8000/redoc/` | Read API documentation |
| **JSON Schema** | `http://localhost:8000/api/api.json/` | Export API schema |
| **Admin Panel** | `http://localhost:8000/admin/` | Manage database |

---

## 🚨 Common Issues

### Issue: Can't access Swagger
**Solution:** Make sure server is running and visit `http://localhost:8000/`

### Issue: Can't login to Admin
**Solution:** Create superuser with `python manage.py createsuperuser`

### Issue: Endpoints not showing in Swagger
**Solution:** Check if `drf-yasg` is installed: `pip install drf-yasg`

### Issue: 404 errors
**Solution:** Check URL is correct and server is running

---

## 🎉 You're All Set!

Now you can:
1. ✅ Test all your APIs in Swagger
2. ✅ Manage your database in Admin
3. ✅ View API documentation in ReDoc
4. ✅ Export API schema for tools

**Happy exploring!** 🚀
