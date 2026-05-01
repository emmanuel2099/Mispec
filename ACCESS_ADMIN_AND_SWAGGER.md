# 🔐 How to Access Django Admin & Swagger UI

## Prerequisites

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Create Superuser (for Admin Access)
```bash
python manage.py createsuperuser
```
Follow the prompts to create:
- Username
- Email
- Password

---

## 🚀 Start the Server

```bash
python manage.py runserver
```

The server will start at: `http://127.0.0.1:8000/` or `http://localhost:8000/`

---

## 📚 Access Swagger UI (API Documentation)

### Swagger UI
**URL:** `http://localhost:8000/`

**Features:**
- Interactive API documentation
- Test endpoints directly in browser
- View request/response schemas
- Try out API calls with authentication

**How to Use:**
1. Open browser and go to `http://localhost:8000/`
2. You'll see all your API endpoints organized by module:
   - **Users** - Authentication endpoints
   - **Profiles** - Profile management endpoints
   - **Chat** - Messaging and call endpoints
3. Click on any endpoint to expand it
4. Click "Try it out" to test the endpoint
5. Fill in parameters and click "Execute"

**Authentication in Swagger:**
1. First, use the `/users/login/` endpoint to get an access token
2. Copy the `access` token from the response
3. Click the "Authorize" button at the top
4. Enter: `Bearer <your_access_token>`
5. Click "Authorize"
6. Now you can test authenticated endpoints

---

## 📖 Access ReDoc (Alternative API Documentation)

**URL:** `http://localhost:8000/redoc/`

**Features:**
- Clean, readable API documentation
- Better for reading/understanding APIs
- Three-panel layout
- Search functionality

---

## 📄 Access JSON Schema

**URL:** `http://localhost:8000/api/api.json/`

**Features:**
- Raw OpenAPI/Swagger JSON schema
- Can be imported into Postman
- Can be used with API testing tools

---

## 🔐 Access Django Admin Panel

### Admin Panel
**URL:** `http://localhost:8000/admin/`

**Login:**
- Username: (the superuser you created)
- Password: (the password you set)

**Features:**
- Manage users
- View/edit profiles
- Manage chat rooms and messages
- View reports and blocks
- Manage gifts and referrals
- View notifications
- Manage events
- View call history

**Available Models in Admin:**

### Users App
- Custom Users
- OTP Checks

### Profiles App
- Profiles
- Profile Media
- Likes
- Matches
- Blocks
- Reports
- Referrals
- Gifts
- Profile Gifts
- Notifications
- Entertainment
- Sport
- Plans
- User Plans

### Chat App
- Chat Rooms
- Messages
- Memberships
- Events
- Call Rooms
- Call Duration
- Message Allowance
- Event Reports

---

## 🎯 Quick Access URLs

Once your server is running at `http://localhost:8000/`:

| Page | URL | Purpose |
|------|-----|---------|
| **Swagger UI** | `http://localhost:8000/` | Interactive API docs |
| **ReDoc** | `http://localhost:8000/redoc/` | Clean API docs |
| **JSON Schema** | `http://localhost:8000/api/api.json/` | Raw API schema |
| **Admin Panel** | `http://localhost:8000/admin/` | Database management |

---

## 🔧 Troubleshooting

### Server Won't Start

**Error: ModuleNotFoundError**
```bash
# Install missing dependencies
pip install -r requirements.txt
```

**Error: Database connection**
```bash
# Check .env file has correct DATABASE_URL
# Run migrations
python manage.py migrate
```

**Error: Port already in use**
```bash
# Use a different port
python manage.py runserver 8080
# Then access at http://localhost:8080/
```

### Can't Login to Admin

**Create a new superuser:**
```bash
python manage.py createsuperuser
```

**Reset password for existing user:**
```bash
python manage.py changepassword <username>
```

### Swagger Not Showing Endpoints

**Check if drf-yasg is installed:**
```bash
pip install drf-yasg
```

**Check urls.py configuration:**
Your `mispec/urls.py` should have:
```python
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="MISPEC API",
      default_version='v1',
      description="Test description",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
```

---

## 📸 What You'll See

### Swagger UI
```
╔══════════════════════════════════════════════════════════╗
║                    MISPEC API                            ║
║                                                          ║
║  [Authorize]                                             ║
║                                                          ║
║  ▼ users - User authentication endpoints                ║
║     POST /users/send_otp/                                ║
║     POST /users/verify_otp/                              ║
║     POST /users/register/                                ║
║     POST /users/login/                                   ║
║     ...                                                  ║
║                                                          ║
║  ▼ profiles - Profile management endpoints              ║
║     POST /profiles/profiles_update/                      ║
║     GET  /profiles/profiles_filter/                      ║
║     ...                                                  ║
║                                                          ║
║  ▼ chat - Messaging and call endpoints                  ║
║     GET  /chat/messages/                                 ║
║     POST /chat/create_room/                              ║
║     ...                                                  ║
╚══════════════════════════════════════════════════════════╝
```

### Django Admin
```
╔══════════════════════════════════════════════════════════╗
║              Django administration                       ║
║                                                          ║
║  Welcome, admin                                          ║
║                                                          ║
║  AUTHENTICATION AND AUTHORIZATION                        ║
║    Users                                                 ║
║    Groups                                                ║
║                                                          ║
║  USERS                                                   ║
║    Custom users                                          ║
║    Otp checks                                            ║
║                                                          ║
║  PROFILES                                                ║
║    Profiles                                              ║
║    Likes                                                 ║
║    Matches                                               ║
║    Blocks                                                ║
║    Reports                                               ║
║    ...                                                   ║
║                                                          ║
║  CHAT                                                    ║
║    Chat rooms                                            ║
║    Messages                                              ║
║    Events                                                ║
║    ...                                                   ║
╚══════════════════════════════════════════════════════════╝
```

---

## 🎓 Tips

### For Swagger UI:
1. **Test Authentication Flow:**
   - Use `/users/register/` to create a test user
   - Use `/users/login/` to get tokens
   - Click "Authorize" and add the token
   - Test other endpoints

2. **View Request/Response:**
   - Each endpoint shows example requests
   - Shows expected response format
   - Shows status codes

3. **Download Schema:**
   - Click "Download" to get OpenAPI spec
   - Import into Postman or other tools

### For Django Admin:
1. **Quick Filters:**
   - Use filters on the right side
   - Search bar at the top
   - Date filters for time-based data

2. **Bulk Actions:**
   - Select multiple items
   - Choose action from dropdown
   - Click "Go"

3. **Inline Editing:**
   - Some models allow inline editing
   - Edit related objects without leaving the page

---

## 🔒 Security Notes

### Production Deployment:
- Change `DEBUG = False` in settings.py
- Set strong `SECRET_KEY`
- Configure `ALLOWED_HOSTS`
- Use HTTPS
- Restrict admin access by IP
- Use strong superuser passwords

### Development:
- Don't commit superuser credentials
- Use different credentials for dev/prod
- Keep `.env` file secure
- Don't expose admin panel publicly

---

## 📞 Need Help?

If you encounter issues:
1. Check Django server logs in terminal
2. Check browser console for errors
3. Verify all dependencies are installed
4. Ensure database is migrated
5. Check `.env` file configuration

---

**Ready to explore your APIs!** 🚀

Start the server and visit:
- **Swagger:** `http://localhost:8000/`
- **Admin:** `http://localhost:8000/admin/`
