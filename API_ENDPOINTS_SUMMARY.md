# MISPEC Backend API Endpoints Summary

## Quick Stats
- **Total Endpoints**: 55
- **Users Module**: 13 endpoints
- **Profiles Module**: 28 endpoints  
- **Chat Module**: 14 endpoints

---

## 📱 Users API (`/users/`)

### Authentication & Registration
| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/users/send_otp/` | POST | ❌ | Send OTP to phone number |
| `/users/verify_otp/` | POST | ❌ | Verify OTP code |
| `/users/register/` | POST | ❌ | Register new user |
| `/users/login/` | POST | ❌ | Login with email/password |
| `/users/logout/` | POST | ✅ | Logout user |
| `/users/api/token/` | POST | ❌ | Obtain JWT token pair |
| `/users/api/token/refresh/` | POST | ❌ | Refresh access token |
| `/users/auth_provider/` | POST | ❌ | Social login (Google, Facebook, etc.) |

### Account Management
| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/users/create_referral/` | POST | ✅ | Create referral code |
| `/users/change_password/` | POST | ✅ | Change user password |
| `/users/reset_password_request/` | POST | ❌ | Request password reset |
| `/users/reset_password_verify/` | POST | ❌ | Verify and reset password |
| `/users/delete_account/` | DELETE | ✅ | Delete user account |

---

## 👤 Profiles API (`/profiles/`)

### Profile Management
| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/profiles/profiles_update/` | POST | ✅ | Update user profile |
| `/profiles/profiles_filter/` | GET | ✅ | Filter profiles by criteria |
| `/profiles/both_profiles_filter/` | GET | ✅ | Filter both male/female profiles |
| `/profiles/media_delete/` | DELETE | ✅ | Delete profile media |

### Discovery & Interests
| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/profiles/entertainment/` | GET | ✅ | Get entertainment preferences |
| `/profiles/sport/` | GET | ✅ | Get sport preferences |

### Interactions
| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/profiles/like_create/` | POST | ✅ | Like a profile |
| `/profiles/liked_profiles/` | GET | ✅ | Get profiles you liked |
| `/profiles/dislike/` | POST | ✅ | Dislike a profile |
| `/profiles/matches/` | GET | ✅ | Get matched profiles |

### Moderation
| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/profiles/report_create/` | POST | ✅ | Report a profile |
| `/profiles/reported_profiles/` | GET | ✅ | Get reported profiles |
| `/profiles/block_create/` | POST | ✅ | Block a profile |
| `/profiles/blocked_profiles/` | GET | ✅ | Get blocked profiles |
| `/profiles/profile_unblock/` | POST | ✅ | Unblock a profile |

### Gifts & Rewards
| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/profiles/gifts/` | GET | ✅ | List available gifts |
| `/profiles/profile_gift/` | POST | ✅ | Create profile gift |
| `/profiles/send_gift/` | POST | ✅ | Send gift to user |
| `/profiles/owned_gift/` | GET | ✅ | Get owned gifts |
| `/profiles/received_gift/` | GET | ✅ | Get received gifts |
| `/profiles/redeem_gift/` | POST | ✅ | Redeem a gift |

### Referrals
| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/profiles/referrals/` | GET | ✅ | Get referral information |
| `/profiles/redeem_referral/` | POST | ✅ | Redeem referral code |

### Notifications
| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/profiles/notifications/` | GET | ✅ | Get all notifications |
| `/profiles/chat_notifications/` | GET | ✅ | Get chat notifications |
| `/profiles/read_notification/` | POST | ✅ | Mark notification as read |

### Payments & Support
| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/profiles/verify_purchase/` | POST | ✅ | Verify in-app purchase |
| `/profiles/support/` | POST | ✅ | Submit support request |

---

## 💬 Chat API (`/chat/`)

### Messaging
| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/chat/messages/` | GET | ✅ | Get messages |
| `/chat/active_chatrooms/` | GET | ✅ | Get active chatrooms |
| `/chat/create_room/` | POST | ✅ | Create chat room |

### Voice/Video Calls
| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/chat/make_call/` | POST | ✅ | Initiate a call |
| `/chat/join_call/` | POST | ✅ | Join an ongoing call |
| `/chat/end_call/` | POST | ✅ | End a call |
| `/chat/call_history/` | GET | ✅ | Get call history |

### Events
| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/chat/create_event/` | POST | ✅ | Create new event |
| `/chat/edit_event/` | PUT | ✅ | Edit existing event |
| `/chat/event_detail/` | GET | ✅ | Get event details |
| `/chat/add_member/` | POST | ✅ | Add member to event |
| `/chat/leave_event/` | POST | ✅ | Leave an event |
| `/chat/stop_event/` | POST | ✅ | Stop/end an event |
| `/chat/report_event/` | POST | ✅ | Report an event |

---

## 🔐 Authentication Flow

```
1. Send OTP → /users/send_otp/
2. Verify OTP → /users/verify_otp/
3. Register → /users/register/
4. Login → /users/login/ (returns access & refresh tokens)
5. Use access token in Authorization header: Bearer <token>
6. Refresh token when expired → /users/api/token/refresh/
```

---

## 📊 API Documentation

### Swagger UI
```
http://localhost:8000/
```

### ReDoc
```
http://localhost:8000/redoc/
```

### JSON Schema
```
http://localhost:8000/api/api.json/
```

---

## 🧪 Testing Tools Provided

### 1. Python Test Script
```bash
# Linux/Mac
./run_api_tests.sh

# Windows
run_api_tests.bat

# Or directly
python test_all_apis.py
```

### 2. Postman Collection
Import `MISPEC_API_Collection.postman_collection.json` into Postman

### 3. Manual Testing
Use Swagger UI at `http://localhost:8000/`

---

## 📝 Common Request Examples

### Login
```json
POST /users/login/
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Update Profile
```json
POST /profiles/profiles_update/
Headers: Authorization: Bearer <token>
{
  "bio": "Hello world",
  "age": 25,
  "gender": "M"
}
```

### Filter Profiles
```json
GET /profiles/profiles_filter/?min_age=18&max_age=35&gender=F
Headers: Authorization: Bearer <token>
```

### Send Message
```json
POST /chat/messages/
Headers: Authorization: Bearer <token>
{
  "recipient_id": 123,
  "message": "Hello!"
}
```

---

## 🔧 Environment Variables

Required in `.env`:
```env
BASE_URL=http://localhost:8000
DATABASE_URL=postgres://...
SECRET_KEY=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AGORA_APP_ID=...
AGORA_APP_CERT=...
```

---

## 📞 Support

- **Email**: dev.team@mispec.co.uk
- **Documentation**: See `API_TEST_README.md`
- **Issues**: Check Django server logs

---

## 🚀 Quick Start

1. **Start Django Server**
   ```bash
   python manage.py runserver
   ```

2. **Run Tests**
   ```bash
   ./run_api_tests.sh  # Linux/Mac
   run_api_tests.bat   # Windows
   ```

3. **View Results**
   - Check terminal output for test results
   - Access Swagger UI for interactive testing
   - Import Postman collection for manual testing

---

**Last Updated**: 2024
**API Version**: v1
