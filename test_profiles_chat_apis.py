"""
Profiles & Chat API Test Script
Logs in first, then tests all authenticated endpoints.
Usage: python test_profiles_chat_apis.py
"""

import requests
import json
import time

BASE_URL = "https://mispec.onrender.com"

RUN_ID = str(int(time.time()))[-6:]
TEST_EMAIL = f"testuser_{RUN_ID}@example.com"
TEST_PHONE = f"+23480{RUN_ID}"
TEST_PASSWORD = "Test1234!"

session = requests.Session()
session.request = lambda method, url, **kwargs: requests.Session.request(session, method, url, timeout=kwargs.pop('timeout', 20), **kwargs)
tokens = {}
state = {}  # stores IDs created during tests
results = []


def log(name, passed, response=None, note=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    code = response.status_code if response else "N/A"
    print(f"{status}  [{code}]  {name}")
    if note:
        print(f"         {note}")
    if not passed and response is not None:
        try:
            print(f"         {response.json()}")
        except Exception:
            print(f"         {response.text[:200]}")
    results.append((name, passed))


def auth_headers():
    return {"Authorization": f"Bearer {tokens['access']}"}


# ─── SETUP: Register + Login ──────────────────────────────────────────────────

def setup():
    print("\n" + "="*55)
    print("SETUP: Registering and logging in test user")
    print("="*55)

    # Send OTP
    r = requests.post(f"{BASE_URL}/users/send_otp/", json={"email": TEST_EMAIL, "phone_number": TEST_PHONE})
    if r.status_code != 200:
        print(f"❌ send_otp failed: {r.status_code} {r.text[:200]}")
        return False
    otp = r.json().get("otp")
    print(f"  OTP: {otp}")

    # Register
    r = requests.post(f"{BASE_URL}/users/register/", json={
        "email": TEST_EMAIL, "phone_number": TEST_PHONE,
        "otp": otp, "password": TEST_PASSWORD
    })
    if r.status_code not in (200, 201):
        print(f"❌ register failed: {r.status_code} {r.text[:200]}")
        return False

    data = r.json()
    tokens["access"] = data.get("tokens", {}).get("access", "")
    tokens["refresh"] = data.get("tokens", {}).get("refresh", "")
    print(f"  Registered & logged in as {TEST_EMAIL}")
    return True


# ─── PROFILES TESTS ───────────────────────────────────────────────────────────

def test_entertainment():
    r = session.get(f"{BASE_URL}/profiles/entertainment/", headers=auth_headers())
    passed = r.status_code == 200
    log("GET /profiles/entertainment/", passed, r)
    if passed:
        data = r.json()
        if data:
            state["entertainment_id"] = data[0].get("id")


def test_sport():
    r = session.get(f"{BASE_URL}/profiles/sport/", headers=auth_headers())
    passed = r.status_code == 200
    log("GET /profiles/sport/", passed, r)
    if passed:
        data = r.json()
        if data:
            state["sport_id"] = data[0].get("id")


def test_profile_update():
    payload = {
        "user": None,  # will be set below
        "first_name": "Test",
        "last_name": "User",
        "bio": "Testing bio",
        "gender": "M",
        "sexual_orientation": "F",
        "date_of_birth": "1995-01-01",
        "latitude": "6.5244",
        "longitude": "3.3792",
    }
    # Get user id first
    r = session.get(f"{BASE_URL}/profiles/profiles_update/", headers=auth_headers())
    if r.status_code == 200:
        user_id = r.json().get("user")
        payload["user"] = user_id

    r = session.patch(f"{BASE_URL}/profiles/profiles_update/", headers=auth_headers(), json=payload)
    passed = r.status_code in (200, 201)
    log("PATCH /profiles/profiles_update/", passed, r)


def test_profile_filter():
    params = {"latitude": "6.5244", "longitude": "3.3792", "distance": "50km", "min_age": "18", "max_age": "40"}
    r = session.get(f"{BASE_URL}/profiles/profiles_filter/", headers=auth_headers(), params=params)
    passed = r.status_code == 200
    log("GET /profiles/profiles_filter/", passed, r,
        f"Found {r.json().get('count', 0)} profiles" if passed else "")


def test_both_profiles_filter():
    params = {"latitude": "6.5244", "longitude": "3.3792", "distance": "50km", "min_age": "18", "max_age": "40"}
    try:
        r = session.get(f"{BASE_URL}/profiles/both_profiles_filter/", headers=auth_headers(), params=params, timeout=30)
        passed = r.status_code == 200
        log("GET /profiles/both_profiles_filter/", passed, r,
            f"Found {r.json().get('count', 0)} profiles" if passed else "")
    except Exception as e:
        log("GET /profiles/both_profiles_filter/", False, note=f"Timeout/error: {e}")


def test_liked_profiles():
    r = session.get(f"{BASE_URL}/profiles/liked_profiles/", headers=auth_headers())
    passed = r.status_code == 200
    log("GET /profiles/liked_profiles/", passed, r)


def test_reported_profiles():
    r = session.get(f"{BASE_URL}/profiles/reported_profiles/", headers=auth_headers())
    passed = r.status_code == 200
    log("GET /profiles/reported_profiles/", passed, r)


def test_blocked_profiles():
    r = session.get(f"{BASE_URL}/profiles/blocked_profiles/", headers=auth_headers())
    passed = r.status_code == 200
    log("GET /profiles/blocked_profiles/", passed, r)


def test_matches():
    r = session.get(f"{BASE_URL}/profiles/matches/", headers=auth_headers())
    passed = r.status_code == 200
    log("GET /profiles/matches/", passed, r,
        f"Found {len(r.json())} matches" if passed else "")


def test_owned_gift():
    r = session.get(f"{BASE_URL}/profiles/owned_gift/", headers=auth_headers())
    passed = r.status_code == 200
    log("GET /profiles/owned_gift/", passed, r)


def test_received_gift():
    r = session.get(f"{BASE_URL}/profiles/received_gift/", headers=auth_headers())
    passed = r.status_code == 200
    log("GET /profiles/received_gift/", passed, r)


def test_referrals():
    r = session.get(f"{BASE_URL}/profiles/referrals/", headers=auth_headers())
    passed = r.status_code == 200
    log("GET /profiles/referrals/", passed, r)


def test_chat_notifications():
    r = session.get(f"{BASE_URL}/profiles/chat_notifications/", headers=auth_headers())
    passed = r.status_code == 200
    log("GET /profiles/chat_notifications/", passed, r)


def test_notifications():
    r = session.get(f"{BASE_URL}/profiles/notifications/", headers=auth_headers())
    passed = r.status_code == 200
    log("GET /profiles/notifications/", passed, r)


def test_gifts_list():
    r = session.get(f"{BASE_URL}/profiles/gifts/", headers=auth_headers())
    passed = r.status_code == 200
    log("GET /profiles/gifts/", passed, r,
        f"Found {len(r.json())} gifts" if passed else "")


def test_support():
    r = session.post(f"{BASE_URL}/profiles/support/", headers=auth_headers(), json={
        "subject": "Test support request",
        "message": "This is an automated test message."
    })
    passed = r.status_code in (200, 201)
    log("POST /profiles/support/", passed, r)


# ─── CHAT TESTS ───────────────────────────────────────────────────────────────

def test_active_chatrooms():
    r = session.get(f"{BASE_URL}/chat/active_chatrooms/", headers=auth_headers())
    passed = r.status_code == 200
    log("GET /chat/active_chatrooms/", passed, r)
    if passed:
        data = r.json()
        private = data.get("private_chat_rooms", [])
        group = data.get("group_chat_rooms", [])
        print(f"         private: {len(private)}, group: {len(group)}")


def test_call_history():
    r = session.get(f"{BASE_URL}/chat/call_history/", headers=auth_headers())
    passed = r.status_code == 200
    log("GET /chat/call_history/", passed, r)


def test_messages_missing_room():
    """GET /chat/messages/ without chat_room_id should return 400"""
    r = session.get(f"{BASE_URL}/chat/messages/", headers=auth_headers())
    passed = r.status_code == 400
    log("GET /chat/messages/ (no room_id → expect 400)", passed, r)


def test_create_event():
    r = session.post(f"{BASE_URL}/chat/create_event/", headers=auth_headers(), json={
        "name": f"Test Event {RUN_ID}",
        "description": "Automated test event",
        "duration": "01:00"
    })
    passed = r.status_code in (200, 201)
    log("POST /chat/create_event/", passed, r)
    if passed:
        data = r.json()
        state["event_id"] = data.get("event_id")
        state["event_room_id"] = data.get("room_id") or data.get("id")
        print(f"         event_id={state.get('event_id')}, room_id={state.get('event_room_id')}")


def test_event_detail():
    event_id = state.get("event_id")
    if not event_id:
        log("GET /chat/event_detail/", False, note="Skipped — no event_id from create_event")
        return
    r = session.get(f"{BASE_URL}/chat/event_detail/", headers=auth_headers(), json={"event_id": str(event_id)})
    passed = r.status_code == 200
    log("GET /chat/event_detail/", passed, r)


def test_edit_event():
    event_id = state.get("event_id")
    if not event_id:
        log("PATCH /chat/edit_event/", False, note="Skipped — no event_id from create_event")
        return
    r = session.patch(f"{BASE_URL}/chat/edit_event/", headers=auth_headers(), json={
        "event_id": str(event_id),
        "name": f"Updated Event {RUN_ID}",
        "description": "Updated description"
    })
    passed = r.status_code == 200
    log("PATCH /chat/edit_event/", passed, r)


def test_stop_event():
    event_id = state.get("event_id")
    if not event_id:
        log("POST /chat/stop_event/", False, note="Skipped — no event_id from create_event")
        return
    r = session.post(f"{BASE_URL}/chat/stop_event/", headers=auth_headers(), json={"event_id": str(event_id)})
    passed = r.status_code == 200
    log("POST /chat/stop_event/", passed, r)


def test_leave_event():
    room_id = state.get("event_room_id")
    if not room_id:
        log("POST /chat/leave_event/", False, note="Skipped — no room_id from create_event")
        return
    r = session.post(f"{BASE_URL}/chat/leave_event/", headers=auth_headers(), json={"chatroom_id": str(room_id)})
    passed = r.status_code == 200
    log("POST /chat/leave_event/", passed, r)


# ─── SUMMARY ──────────────────────────────────────────────────────────────────

def summary():
    print("\n" + "="*55)
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"Results: {passed}/{total} passed")
    if passed < total:
        print("Failed:")
        for name, p in results:
            if not p:
                print(f"  ✗ {name}")
    print("="*55)


if __name__ == "__main__":
    print(f"\nTesting Profiles & Chat APIs at: {BASE_URL}\n" + "-"*55)

    if not setup():
        print("❌ Setup failed — cannot continue")
        exit(1)

    print("\n" + "="*55)
    print("PROFILES ENDPOINTS")
    print("="*55)
    test_entertainment()
    test_sport()
    test_profile_update()
    test_profile_filter()
    test_both_profiles_filter()
    test_liked_profiles()
    test_reported_profiles()
    test_blocked_profiles()
    test_matches()
    test_owned_gift()
    test_received_gift()
    test_referrals()
    test_chat_notifications()
    test_notifications()
    test_gifts_list()
    test_support()

    print("\n" + "="*55)
    print("CHAT ENDPOINTS")
    print("="*55)
    test_active_chatrooms()
    test_call_history()
    test_messages_missing_room()
    test_create_event()
    test_event_detail()
    test_edit_event()
    test_stop_event()
    test_leave_event()

    summary()
