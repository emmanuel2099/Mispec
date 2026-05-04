"""
Auth API Test Script
Tests all /users/ endpoints against the live server.
Usage: python test_auth_apis.py
"""

import requests
import json
import sys

BASE_URL = "http://146.190.171.123:8000"

# Test credentials — change these as needed
TEST_EMAIL = "testuser_auth@example.com"
TEST_PHONE = "+2348012345678"
TEST_PASSWORD = "Test1234!"
TEST_OTP = ""  # Will be filled after send_otp

# Shared state across tests
tokens = {}
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


def test_send_otp():
    r = requests.post(f"{BASE_URL}/users/send_otp/", json={
        "email": TEST_EMAIL,
        "phone_number": TEST_PHONE
    })
    passed = r.status_code == 200
    log("POST /users/send_otp/", passed, r, "Check email/SMS for OTP")
    return passed


def test_verify_otp(otp_code):
    r = requests.post(f"{BASE_URL}/users/verify_otp/", json={
        "email": TEST_EMAIL,
        "otp_code": otp_code
    })
    passed = r.status_code == 200
    log("POST /users/verify_otp/", passed, r)
    return passed


def test_register(otp_code):
    r = requests.post(f"{BASE_URL}/users/register/", json={
        "email": TEST_EMAIL,
        "phone_number": TEST_PHONE,
        "otp": otp_code,
        "password": TEST_PASSWORD
    })
    passed = r.status_code == 201
    log("POST /users/register/", passed, r)
    if passed:
        data = r.json()
        tokens["access"] = data.get("tokens", {}).get("access", "")
        tokens["refresh"] = data.get("tokens", {}).get("refresh", "")
    return passed


def test_login():
    r = requests.post(f"{BASE_URL}/users/login/", json={
        "phone_number": TEST_PHONE,
        "password": TEST_PASSWORD
    })
    passed = r.status_code == 200
    log("POST /users/login/", passed, r)
    if passed:
        data = r.json()
        tokens["access"] = data.get("tokens", {}).get("access", "")
        tokens["refresh"] = data.get("tokens", {}).get("refresh", "")
    return passed


def test_token_refresh():
    if not tokens.get("refresh"):
        log("POST /users/api/token/refresh/", False, note="No refresh token available")
        return False
    r = requests.post(f"{BASE_URL}/users/api/token/refresh/", json={
        "refresh": tokens["refresh"]
    })
    passed = r.status_code == 200
    log("POST /users/api/token/refresh/", passed, r)
    return passed


def test_change_password():
    if not tokens.get("access"):
        log("POST /users/change_password/", False, note="No access token")
        return False
    headers = {"Authorization": f"Bearer {tokens['access']}"}
    r = requests.post(f"{BASE_URL}/users/change_password/", json={
        "old_password": TEST_PASSWORD,
        "new_password": TEST_PASSWORD  # keep same for subsequent tests
    }, headers=headers)
    passed = r.status_code == 200
    log("POST /users/change_password/", passed, r)
    return passed


def test_reset_password_request():
    r = requests.post(f"{BASE_URL}/users/reset_password_request/", json={
        "email": TEST_EMAIL,
        "phone_number": TEST_PHONE
    })
    passed = r.status_code == 200
    log("POST /users/reset_password_request/", passed, r)
    otp = None
    if passed:
        otp = r.json().get("otp")
        print(f"         OTP from response: {otp}")
    return passed, otp


def test_reset_password_verify(otp_code):
    r = requests.post(f"{BASE_URL}/users/reset_password_verify/", json={
        "phone_number": TEST_PHONE,
        "new_password": TEST_PASSWORD
    })
    passed = r.status_code == 200
    log("POST /users/reset_password_verify/", passed, r)
    return passed


def test_provider_auth_new_user(provider):
    """Test first-time sign-in via Google or Facebook (creates new user)"""
    r = requests.post(f"{BASE_URL}/users/auth_provider/", json={
        "provider": provider,
        "provider_id": f"fake_{provider}_id_99999",
        "email": f"test_{provider}_new@example.com",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": f"+234801000{'1111' if provider == 'google' else '2222'}"
    })
    passed = r.status_code == 200
    log(f"POST /users/auth_provider/ ({provider} - new user)", passed, r)
    if passed:
        data = r.json()
        tokens["access"] = data.get("tokens", {}).get("access", tokens.get("access", ""))
        tokens["refresh"] = data.get("tokens", {}).get("refresh", tokens.get("refresh", ""))
    return passed


def test_provider_auth_existing_user(provider):
    """Test sign-in for already registered provider user"""
    r = requests.post(f"{BASE_URL}/users/auth_provider/", json={
        "provider": provider,
        "provider_id": f"fake_{provider}_id_99999",
    })
    passed = r.status_code == 200
    log(f"POST /users/auth_provider/ ({provider} - existing user)", passed, r)
    return passed


def test_logout():
    if not tokens.get("access") or not tokens.get("refresh"):
        log("POST /users/logout/", False, note="No tokens available")
        return False
    headers = {"Authorization": f"Bearer {tokens['access']}"}
    r = requests.post(f"{BASE_URL}/users/logout/", json={
        "refresh_token": tokens["refresh"]
    }, headers=headers)
    passed = r.status_code == 200
    log("POST /users/logout/", passed, r)
    return passed


def test_delete_account():
    # Re-login first since logout invalidated tokens
    login_r = requests.post(f"{BASE_URL}/users/login/", json={
        "phone_number": TEST_PHONE,
        "password": TEST_PASSWORD
    })
    if login_r.status_code != 200:
        log("POST /users/delete_account/", False, note="Could not re-login to test delete")
        return False
    access = login_r.json().get("tokens", {}).get("access", "")
    headers = {"Authorization": f"Bearer {access}"}
    r = requests.post(f"{BASE_URL}/users/delete_account/", json={}, headers=headers)
    passed = r.status_code == 200
    log("POST /users/delete_account/", passed, r)
    return passed


def summary():
    print("\n" + "="*50)
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"Results: {passed}/{total} passed")
    if passed < total:
        print("Failed:")
        for name, p in results:
            if not p:
                print(f"  - {name}")
    print("="*50)


if __name__ == "__main__":
    print(f"\nTesting Auth APIs at: {BASE_URL}\n" + "-"*50)

    # Step 1: Send OTP
    if not test_send_otp():
        print("\n⚠️  send_otp failed. Enter OTP manually or check server.")

    # Step 2: Get OTP from user input
    otp = input("\nEnter OTP received (email/SMS): ").strip()

    # Step 3: Verify OTP
    test_verify_otp(otp)

    # Step 4: Register
    registered = test_register(otp)

    # Step 5: Login (also works if already registered)
    if not registered:
        print("         (trying login with existing account...)")
    test_login()

    # Step 6: Token refresh
    test_token_refresh()

    # Step 7: Change password
    test_change_password()

    # Step 8: Reset password request
    _, reset_otp = test_reset_password_request()

    # Step 9: Reset password verify
    test_reset_password_verify(reset_otp)

    # Step 10: Logout
    test_logout()

    # Step 11: Google auth - new user
    test_provider_auth_new_user("google")

    # Step 12: Google auth - existing user (same provider_id)
    test_provider_auth_existing_user("google")

    # Step 13: Facebook auth - new user
    test_provider_auth_new_user("facebook")

    # Step 14: Facebook auth - existing user
    test_provider_auth_existing_user("facebook")

    # Step 11: Delete account (optional — comment out to keep test user)
    # test_delete_account()

    summary()
