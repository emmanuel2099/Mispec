"""
Full API Test Suite — tests all endpoints against Render
Usage: python test_all_apis_render.py
"""

import requests
import time

BASE_URL = "https://mispec.onrender.com"

RUN_ID = str(int(time.time()))[-6:]
TEST_EMAIL = f"testuser_{RUN_ID}@example.com"
TEST_PHONE = f"+23480{RUN_ID}"
TEST_PASSWORD = "Test1234!"

tokens = {}
profile_id = None
chat_room_id = None
event_id = None
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


def auth():
    headers = {"Authorization": f"Bearer {tokens.get('access', '')}"}
    return headers


# ─── AUTH ────────────────────────────────────────────────────────────────────

def test_send_otp():
    r = requests.post(f"{BASE_URL}/users/send_otp/", json={"email": TEST_EMAIL, "phone_number": TEST_PHONE})
    passed = r.status_code == 200
    log("POST /users/send_otp/", passed, r)
    otp = r.json().get("otp") if passed else None
    if otp:
        print(f"         OTP: {otp}")
    return passed, otp

def test_verify_otp(otp):
    r = requests.post(f"{BASE_URL}/users/verify_otp/", json={"email": TEST_EMAIL, "otp_code": otp})
    passed = r.status_code == 200
    log("POST /users/verify_otp/", passed, r)
    return passed

def test_register(otp):
    r = requests.post(f"{BASE_URL}/users/register/", json={"email": TEST_EMAIL, "phone_number": TEST_PHONE, "otp": otp, "password": TEST_PASSWORD})
    passed = r.status_code == 201
    log("POST /users/register/", passed, r)
    if passed:
        tokens["access"] = r.json().get("tokens", {}).get("access", "")
        tokens["refresh"] = r.json().get("tokens", {}).get("refresh", "")
    return passed

def test_login():
    r = requests.post(f"{BASE_URL}/users/login/", json={"phone_number": TEST_PHONE, "password": TEST_PASSWORD})
    passed = r.status_code == 200
    log("POST /users/login/", passed, r)
    if passed:
        tokens["access"] = r.json().get("tokens", {}).get("access", "")
        tokens["refresh"] = r.json().get("tokens", {}).get("refresh", "")
    return passed

def test_token_refresh():
    r = requests.post(f"{BASE_URL}/users/api/token/refresh/", json={"refresh": tokens.get("refresh", "")})
    passed = r.status_code == 200
    log("POST /users/api/token/refresh/", passed, r)
    return passed

def test_change_password():
    r = requests.post(f"{BASE_URL}/users/change_password/", json={"old_password": TEST_PASSWORD, "new_password": TEST_PASSWORD}, headers=auth())
    passed = r.status_code == 200
    log("POST /users/change_password/", passed, r)
    return passed

def test_reset_password_request():
    r = requests.post(f"{BASE_URL}/users/reset_password_request/", json={"email": TEST_EMAIL, "phone_number": TEST_PHONE})
    passed = r.status_code == 200
    log("POST /users/reset_password_request/", passed, r)
    return passed

def test_reset_password_verify():
    r = requests.post(f"{BASE_URL}/users/reset_password_verify/", json={"phone_number": TEST_PHONE, "new_password": TEST_PASSWORD})
    passed = r.status_code == 200
    log("POST /users/reset_password_verify/", passed, r)
    return passed

def test_logout():
    login_r = requests.post(f"{BASE_URL}/users/login/", json={"phone_number": TEST_PHONE, "password": TEST_PASSWORD})
    if login_r.status_code != 200:
        log("POST /users/logout/", False, note="Re-login failed")
        return False
    fresh_access = login_r.json().get("tokens", {}).get("access", "")
    fresh_refresh = login_r.json().get("tokens", {}).get("refresh", "")
    r = requests.post(f"{BASE_URL}/users/logout/", json={"refresh_token": fresh_refresh}, headers={"Authorization": f"Bearer {fresh_access}"})
    passed = r.status_code == 200
    log("POST /users/logout/", passed, r)
    return passed

def test_provider_auth(provider, new_user=True):
    payload = {"provider": provider, "provider_id": f"fake_{provider}_render_{RUN_ID}"}
    if new_user:
        phone_suffix = "1111" if provider == "google" else "2222"
        payload.update({
            "email": f"test_{provider}_{RUN_ID}@example.com",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": f"+2348{phone_suffix}{RUN_ID}"
        })
    r = requests.post(f"{BASE_URL}/users/auth_provider/", json=payload)
    passed = r.status_code == 200
    label = "new user" if new_user else "existing user"
    log(f"POST /users/auth_provider/ ({provider} - {label})", passed, r)
    return passed


# ─── PROFILES ────────────────────────────────────────────────────────────────

def test_get_profile():
    r = requests.get(f"{BASE_URL}/profiles/profiles_update/", headers=auth())
    passed = r.status_code == 200
    log("GET /profiles/profiles_update/", passed, r)
    if passed:
        global profile_id
        profile_id = r.json().get("id")
    return passed

def test_entertainment():
    r = requests.get(f"{BASE_URL}/profiles/entertainment/", headers=auth())
    passed = r.status_code == 200
    log("GET /profiles/entertainment/", passed, r)
    return passed

def test_sport():
    r = requests.get(f"{BASE_URL}/profiles/sport/", headers=auth())
    passed = r.status_code == 200
    log("GET /profiles/sport/", passed, r)
    return passed

def test_gifts_list():
    r = requests.get(f"{BASE_URL}/profiles/gifts/", headers=auth())
    passed = r.status_code == 200
    log("GET /profiles/gifts/", passed, r)
    return passed

def test_liked_profiles():
    r = requests.get(f"{BASE_URL}/profiles/liked_profiles/", headers=auth())
    passed = r.status_code == 200
    log("GET /profiles/liked_profiles/", passed, r)
    return passed

def test_matches():
    r = requests.get(f"{BASE_URL}/profiles/matches/", headers=auth())
    passed = r.status_code == 200
    log("GET /profiles/matches/", passed, r)
    return passed

def test_blocked_profiles():
    r = requests.get(f"{BASE_URL}/profiles/blocked_profiles/", headers=auth())
    passed = r.status_code == 200
    log("GET /profiles/blocked_profiles/", passed, r)
    return passed

def test_reported_profiles():
    r = requests.get(f"{BASE_URL}/profiles/reported_profiles/", headers=auth())
    passed = r.status_code == 200
    log("GET /profiles/reported_profiles/", passed, r)
    return passed

def test_referrals():
    r = requests.get(f"{BASE_URL}/profiles/referrals/", headers=auth())
    passed = r.status_code == 200
    log("GET /profiles/referrals/", passed, r)
    return passed

def test_owned_gifts():
    r = requests.get(f"{BASE_URL}/profiles/owned_gift/", headers=auth())
    passed = r.status_code == 200
    log("GET /profiles/owned_gift/", passed, r)
    return passed

def test_received_gifts():
    r = requests.get(f"{BASE_URL}/profiles/received_gift/", headers=auth())
    passed = r.status_code == 200
    log("GET /profiles/received_gift/", passed, r)
    return passed

def test_notifications():
    r = requests.get(f"{BASE_URL}/profiles/notifications/", headers=auth())
    passed = r.status_code == 200
    log("GET /profiles/notifications/", passed, r)
    return passed

def test_chat_notifications():
    r = requests.get(f"{BASE_URL}/profiles/chat_notifications/", headers=auth())
    passed = r.status_code == 200
    log("GET /profiles/chat_notifications/", passed, r)
    return passed

def test_read_notifications():
    r = requests.post(f"{BASE_URL}/profiles/read_notification/", json={}, headers=auth())
    passed = r.status_code == 200
    log("POST /profiles/read_notification/", passed, r)
    return passed

def test_support():
    r = requests.post(f"{BASE_URL}/profiles/support/", json={"description": "Test support request"}, headers=auth())
    passed = r.status_code in (200, 201)
    log("POST /profiles/support/", passed, r)
    return passed

def test_profiles_filter():
    r = requests.get(f"{BASE_URL}/profiles/profiles_filter/?latitude=6.5244&longitude=3.3792&distance=10km&min_age=18&max_age=40", headers=auth())
    passed = r.status_code in (200, 400)  # 400 if no location set on profile
    log("GET /profiles/profiles_filter/", passed, r, "400 is ok if profile has no location set")
    return passed


# ─── CHAT ────────────────────────────────────────────────────────────────────

def test_active_chatrooms():
    r = requests.get(f"{BASE_URL}/chat/active_chatrooms/", headers=auth())
    passed = r.status_code == 200
    log("GET /chat/active_chatrooms/", passed, r)
    return passed

def test_create_event():
    r = requests.post(f"{BASE_URL}/chat/create_event/", json={"name": f"Test Event {RUN_ID}", "description": "Test", "duration": "01:00"}, headers=auth())
    passed = r.status_code == 201
    log("POST /chat/create_event/", passed, r)
    if passed:
        global chat_room_id, event_id
        chat_room_id = str(r.json().get("room_id", ""))
        event_id = str(r.json().get("event_id", ""))
    return passed

def test_stop_event():
    if not event_id:
        log("POST /chat/stop_event/", False, note="No event_id")
        return False
    r = requests.post(f"{BASE_URL}/chat/stop_event/", json={"event_id": event_id}, headers=auth())
    passed = r.status_code == 200
    log("POST /chat/stop_event/", passed, r)
    return passed

def test_call_history():
    if not chat_room_id:
        log("GET /chat/call_history/", False, note="No chat_room_id")
        return False
    r = requests.get(f"{BASE_URL}/chat/call_history/", json={"chatroom_id": chat_room_id}, headers=auth())
    passed = r.status_code == 200
    log("GET /chat/call_history/", passed, r)
    return passed


# ─── SUMMARY ─────────────────────────────────────────────────────────────────

def summary():
    print("\n" + "="*55)
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"Results: {passed}/{total} passed")
    if passed < total:
        print("Failed:")
        for name, p in results:
            if not p:
                print(f"  - {name}")
    print("="*55)


if __name__ == "__main__":
    print(f"\nTesting ALL APIs at: {BASE_URL}\n" + "-"*55)

    # Auth
    print("\n── AUTH ──")
    _, otp = test_send_otp()
    if not otp:
        otp = input("Enter OTP manually: ").strip()
    test_verify_otp(otp)
    registered = test_register(otp)
    if not registered:
        test_login()
    else:
        test_login()
    test_token_refresh()
    test_change_password()
    test_reset_password_request()
    test_reset_password_verify()
    test_logout()
    test_provider_auth("google", new_user=True)
    test_provider_auth("google", new_user=False)
    test_provider_auth("facebook", new_user=True)
    test_provider_auth("facebook", new_user=False)

    # Re-login to get fresh token for remaining tests
    requests.post(f"{BASE_URL}/users/login/", json={"phone_number": TEST_PHONE, "password": TEST_PASSWORD})
    login_r = requests.post(f"{BASE_URL}/users/login/", json={"phone_number": TEST_PHONE, "password": TEST_PASSWORD})
    if login_r.status_code == 200:
        tokens["access"] = login_r.json().get("tokens", {}).get("access", "")
        tokens["refresh"] = login_r.json().get("tokens", {}).get("refresh", "")

    # Profiles
    print("\n── PROFILES ──")
    test_get_profile()
    test_entertainment()
    test_sport()
    test_gifts_list()
    test_liked_profiles()
    test_matches()
    test_blocked_profiles()
    test_reported_profiles()
    test_referrals()
    test_owned_gifts()
    test_received_gifts()
    test_notifications()
    test_chat_notifications()
    test_read_notifications()
    test_support()
    test_profiles_filter()

    # Chat
    print("\n── CHAT ──")
    test_active_chatrooms()
    test_create_event()
    test_stop_event()
    test_call_history()

    summary()
