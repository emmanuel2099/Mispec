"""
Comprehensive API Testing Script for MISPEC Backend
Tests all endpoints from users, profiles, and chat apps
"""

import requests
import json
from typing import Dict, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base URL - Update this to your actual backend URL
BASE_URL = os.getenv('BASE_URL', 'http://localhost:8000')

# Test data storage
test_data = {
    'access_token': None,
    'refresh_token': None,
    'user_id': None,
    'phone_number': '+1234567890',  # Update with valid test phone
    'otp_code': None,
    'test_email': 'test@example.com',
    'test_password': 'TestPass123!',
}


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_test_header(section: str):
    """Print formatted section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{section.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")


def print_result(endpoint: str, method: str, status_code: int, success: bool, message: str = ""):
    """Print formatted test result"""
    status_color = Colors.GREEN if success else Colors.RED
    status_text = "✓ PASS" if success else "✗ FAIL"
    print(f"{status_color}{status_text}{Colors.RESET} | {method:6} | {endpoint:50} | Status: {status_code} | {message}")


def get_headers(auth: bool = False) -> Dict[str, str]:
    """Get request headers with optional authentication"""
    headers = {'Content-Type': 'application/json'}
    if auth and test_data['access_token']:
        headers['Authorization'] = f'Bearer {test_data["access_token"]}'
    return headers


def test_endpoint(method: str, endpoint: str, data: Optional[Dict] = None, 
                  auth: bool = False, expected_status: int = 200) -> tuple:
    """
    Test an API endpoint
    Returns: (success: bool, status_code: int, response_data: dict)
    """
    url = f"{BASE_URL}{endpoint}"
    headers = get_headers(auth)
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=data, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, json=data, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, json=data, timeout=10)
        else:
            return False, 0, {}
        
        success = response.status_code == expected_status or (200 <= response.status_code < 300)
        
        try:
            response_data = response.json()
        except:
            response_data = {'text': response.text}
        
        return success, response.status_code, response_data
    
    except requests.exceptions.Timeout:
        return False, 0, {'error': 'Request timeout'}
    except requests.exceptions.ConnectionError:
        return False, 0, {'error': 'Connection error'}
    except Exception as e:
        return False, 0, {'error': str(e)}


# ============================================================================
# USER AUTHENTICATION TESTS
# ============================================================================

def test_users_endpoints():
    """Test all /users/ endpoints"""
    print_test_header("USERS API TESTS")
    
    # 1. Send OTP
    print(f"\n{Colors.YELLOW}1. Testing OTP Flow{Colors.RESET}")
    success, status, data = test_endpoint(
        'POST', '/users/send_otp/',
        {'phone_number': test_data['phone_number']},
        expected_status=200
    )
    print_result('/users/send_otp/', 'POST', status, success, 
                 "OTP sent" if success else data.get('error', ''))
    
    # 2. Verify OTP (requires manual OTP input)
    print(f"\n{Colors.YELLOW}Note: OTP verification requires actual OTP code{Colors.RESET}")
    print_result('/users/verify_otp/', 'POST', 0, False, "Skipped - requires manual OTP")
    
    # 3. Register User
    print(f"\n{Colors.YELLOW}2. Testing User Registration{Colors.RESET}")
    register_data = {
        'email': test_data['test_email'],
        'password': test_data['test_password'],
        'phone_number': test_data['phone_number'],
        'first_name': 'Test',
        'last_name': 'User'
    }
    success, status, data = test_endpoint(
        'POST', '/users/register/',
        register_data,
        expected_status=201
    )
    print_result('/users/register/', 'POST', status, success,
                 "User registered" if success else data.get('error', ''))
    
    # 4. Login
    print(f"\n{Colors.YELLOW}3. Testing User Login{Colors.RESET}")
    login_data = {
        'email': test_data['test_email'],
        'password': test_data['test_password']
    }
    success, status, data = test_endpoint(
        'POST', '/users/login/',
        login_data
    )
    if success and 'access' in data:
        test_data['access_token'] = data['access']
        test_data['refresh_token'] = data.get('refresh')
        print_result('/users/login/', 'POST', status, True, "Login successful, token saved")
    else:
        print_result('/users/login/', 'POST', status, success, data.get('error', ''))
    
    # 5. Token Refresh
    print(f"\n{Colors.YELLOW}4. Testing Token Refresh{Colors.RESET}")
    if test_data['refresh_token']:
        success, status, data = test_endpoint(
            'POST', '/users/api/token/refresh/',
            {'refresh': test_data['refresh_token']}
        )
        print_result('/users/api/token/refresh/', 'POST', status, success)
    else:
        print_result('/users/api/token/refresh/', 'POST', 0, False, "Skipped - no refresh token")
    
    # 6. Provider Auth (Social Login)
    print(f"\n{Colors.YELLOW}5. Testing Provider Auth{Colors.RESET}")
    print_result('/users/auth_provider/', 'POST', 0, False, "Skipped - requires OAuth tokens")
    
    # 7. Create Referral
    print(f"\n{Colors.YELLOW}6. Testing Create Referral{Colors.RESET}")
    success, status, data = test_endpoint(
        'POST', '/users/create_referral/',
        {'referral_code': 'TEST123'},
        auth=True
    )
    print_result('/users/create_referral/', 'POST', status, success)
    
    # 8. Change Password
    print(f"\n{Colors.YELLOW}7. Testing Change Password{Colors.RESET}")
    change_pwd_data = {
        'old_password': test_data['test_password'],
        'new_password': 'NewTestPass123!'
    }
    success, status, data = test_endpoint(
        'POST', '/users/change_password/',
        change_pwd_data,
        auth=True
    )
    print_result('/users/change_password/', 'POST', status, success)
    
    # 9. Reset Password Request
    print(f"\n{Colors.YELLOW}8. Testing Reset Password Request{Colors.RESET}")
    success, status, data = test_endpoint(
        'POST', '/users/reset_password_request/',
        {'email': test_data['test_email']}
    )
    print_result('/users/reset_password_request/', 'POST', status, success)
    
    # 10. Reset Password Verify
    print(f"\n{Colors.YELLOW}9. Testing Reset Password Verify{Colors.RESET}")
    print_result('/users/reset_password_verify/', 'POST', 0, False, "Skipped - requires reset token")
    
    # 11. Logout
    print(f"\n{Colors.YELLOW}10. Testing Logout{Colors.RESET}")
    success, status, data = test_endpoint(
        'POST', '/users/logout/',
        {'refresh_token': test_data['refresh_token']},
        auth=True
    )
    print_result('/users/logout/', 'POST', status, success)
    
    # 12. Delete Account
    print(f"\n{Colors.YELLOW}11. Testing Delete Account{Colors.RESET}")
    print_result('/users/delete_account/', 'DELETE', 0, False, "Skipped - destructive operation")


# ============================================================================
# PROFILES API TESTS
# ============================================================================

def test_profiles_endpoints():
    """Test all /profiles/ endpoints"""
    print_test_header("PROFILES API TESTS")
    
    # 1. Profile Update
    print(f"\n{Colors.YELLOW}1. Testing Profile Update{Colors.RESET}")
    profile_data = {
        'bio': 'Test bio',
        'age': 25,
        'gender': 'M'
    }
    success, status, data = test_endpoint(
        'POST', '/profiles/profiles_update/',
        profile_data,
        auth=True
    )
    print_result('/profiles/profiles_update/', 'POST', status, success)
    
    # 2. Profile Filter
    print(f"\n{Colors.YELLOW}2. Testing Profile Filter{Colors.RESET}")
    filter_data = {
        'min_age': 18,
        'max_age': 35,
        'gender': 'F'
    }
    success, status, data = test_endpoint(
        'GET', '/profiles/profiles_filter/',
        filter_data,
        auth=True
    )
    print_result('/profiles/profiles_filter/', 'GET', status, success)
    
    # 3. Both Profile Filter
    print(f"\n{Colors.YELLOW}3. Testing Both Profile Filter{Colors.RESET}")
    success, status, data = test_endpoint(
        'GET', '/profiles/both_profiles_filter/',
        filter_data,
        auth=True
    )
    print_result('/profiles/both_profiles_filter/', 'GET', status, success)
    
    # 4. Entertainment
    print(f"\n{Colors.YELLOW}4. Testing Entertainment{Colors.RESET}")
    success, status, data = test_endpoint(
        'GET', '/profiles/entertainment/',
        auth=True
    )
    print_result('/profiles/entertainment/', 'GET', status, success)
    
    # 5. Sport
    print(f"\n{Colors.YELLOW}5. Testing Sport{Colors.RESET}")
    success, status, data = test_endpoint(
        'GET', '/profiles/sport/',
        auth=True
    )
    print_result('/profiles/sport/', 'GET', status, success)
    
    # 6. Media Delete
    print(f"\n{Colors.YELLOW}6. Testing Media Delete{Colors.RESET}")
    print_result('/profiles/media_delete/', 'DELETE', 0, False, "Skipped - requires media ID")
    
    # 7. Like Create
    print(f"\n{Colors.YELLOW}7. Testing Like Create{Colors.RESET}")
    print_result('/profiles/like_create/', 'POST', 0, False, "Skipped - requires profile ID")
    
    # 8. Liked Profiles
    print(f"\n{Colors.YELLOW}8. Testing Liked Profiles{Colors.RESET}")
    success, status, data = test_endpoint(
        'GET', '/profiles/liked_profiles/',
        auth=True
    )
    print_result('/profiles/liked_profiles/', 'GET', status, success)
    
    # 9. Report Create
    print(f"\n{Colors.YELLOW}9. Testing Report Create{Colors.RESET}")
    print_result('/profiles/report_create/', 'POST', 0, False, "Skipped - requires profile ID")
    
    # 10. Reported Profiles
    print(f"\n{Colors.YELLOW}10. Testing Reported Profiles{Colors.RESET}")
    success, status, data = test_endpoint(
        'GET', '/profiles/reported_profiles/',
        auth=True
    )
    print_result('/profiles/reported_profiles/', 'GET', status, success)
    
    # 11. Block Create
    print(f"\n{Colors.YELLOW}11. Testing Block Create{Colors.RESET}")
    print_result('/profiles/block_create/', 'POST', 0, False, "Skipped - requires profile ID")
    
    # 12. Blocked Profiles
    print(f"\n{Colors.YELLOW}12. Testing Blocked Profiles{Colors.RESET}")
    success, status, data = test_endpoint(
        'GET', '/profiles/blocked_profiles/',
        auth=True
    )
    print_result('/profiles/blocked_profiles/', 'GET', status, success)
    
    # 13. Matches
    print(f"\n{Colors.YELLOW}13. Testing Matches{Colors.RESET}")
    success, status, data = test_endpoint(
        'GET', '/profiles/matches/',
        auth=True
    )
    print_result('/profiles/matches/', 'GET', status, success)
    
    # 14. Profile Gift
    print(f"\n{Colors.YELLOW}14. Testing Profile Gift{Colors.RESET}")
    print_result('/profiles/profile_gift/', 'POST', 0, False, "Skipped - requires gift data")
    
    # 15. Owned Gift
    print(f"\n{Colors.YELLOW}15. Testing Owned Gift{Colors.RESET}")
    success, status, data = test_endpoint(
        'GET', '/profiles/owned_gift/',
        auth=True
    )
    print_result('/profiles/owned_gift/', 'GET', status, success)
    
    # 16. Received Gift
    print(f"\n{Colors.YELLOW}16. Testing Received Gift{Colors.RESET}")
    success, status, data = test_endpoint(
        'GET', '/profiles/received_gift/',
        auth=True
    )
    print_result('/profiles/received_gift/', 'GET', status, success)
    
    # 17. Profile Unblock
    print(f"\n{Colors.YELLOW}17. Testing Profile Unblock{Colors.RESET}")
    print_result('/profiles/profile_unblock/', 'POST', 0, False, "Skipped - requires profile ID")
    
    # 18. Referrals
    print(f"\n{Colors.YELLOW}18. Testing Referrals{Colors.RESET}")
    success, status, data = test_endpoint(
        'GET', '/profiles/referrals/',
        auth=True
    )
    print_result('/profiles/referrals/', 'GET', status, success)
    
    # 19. Redeem Gift
    print(f"\n{Colors.YELLOW}19. Testing Redeem Gift{Colors.RESET}")
    print_result('/profiles/redeem_gift/', 'POST', 0, False, "Skipped - requires gift code")
    
    # 20. Redeem Referral
    print(f"\n{Colors.YELLOW}20. Testing Redeem Referral{Colors.RESET}")
    print_result('/profiles/redeem_referral/', 'POST', 0, False, "Skipped - requires referral code")
    
    # 21. Dislike
    print(f"\n{Colors.YELLOW}21. Testing Dislike{Colors.RESET}")
    print_result('/profiles/dislike/', 'POST', 0, False, "Skipped - requires profile ID")
    
    # 22. Chat Notifications
    print(f"\n{Colors.YELLOW}22. Testing Chat Notifications{Colors.RESET}")
    success, status, data = test_endpoint(
        'GET', '/profiles/chat_notifications/',
        auth=True
    )
    print_result('/profiles/chat_notifications/', 'GET', status, success)
    
    # 23. Notifications
    print(f"\n{Colors.YELLOW}23. Testing Notifications{Colors.RESET}")
    success, status, data = test_endpoint(
        'GET', '/profiles/notifications/',
        auth=True
    )
    print_result('/profiles/notifications/', 'GET', status, success)
    
    # 24. Read Notification
    print(f"\n{Colors.YELLOW}24. Testing Read Notification{Colors.RESET}")
    print_result('/profiles/read_notification/', 'POST', 0, False, "Skipped - requires notification ID")
    
    # 25. Send Gift
    print(f"\n{Colors.YELLOW}25. Testing Send Gift{Colors.RESET}")
    print_result('/profiles/send_gift/', 'POST', 0, False, "Skipped - requires gift and recipient data")
    
    # 26. Gifts List
    print(f"\n{Colors.YELLOW}26. Testing Gifts List{Colors.RESET}")
    success, status, data = test_endpoint(
        'GET', '/profiles/gifts/',
        auth=True
    )
    print_result('/profiles/gifts/', 'GET', status, success)
    
    # 27. Verify Purchase
    print(f"\n{Colors.YELLOW}27. Testing Verify Purchase{Colors.RESET}")
    print_result('/profiles/verify_purchase/', 'POST', 0, False, "Skipped - requires purchase data")
    
    # 28. Support
    print(f"\n{Colors.YELLOW}28. Testing Support{Colors.RESET}")
    support_data = {
        'subject': 'Test Support Request',
        'message': 'This is a test message'
    }
    success, status, data = test_endpoint(
        'POST', '/profiles/support/',
        support_data,
        auth=True
    )
    print_result('/profiles/support/', 'POST', status, success)


# ============================================================================
# CHAT API TESTS
# ============================================================================

def test_chat_endpoints():
    """Test all /chat/ endpoints"""
    print_test_header("CHAT API TESTS")
    
    # 1. Messages
    print(f"\n{Colors.YELLOW}1. Testing Messages{Colors.RESET}")
    success, status, data = test_endpoint(
        'GET', '/chat/messages/',
        auth=True
    )
    print_result('/chat/messages/', 'GET', status, success)
    
    # 2. Active Chatrooms
    print(f"\n{Colors.YELLOW}2. Testing Active Chatrooms{Colors.RESET}")
    success, status, data = test_endpoint(
        'GET', '/chat/active_chatrooms/',
        auth=True
    )
    print_result('/chat/active_chatrooms/', 'GET', status, success)
    
    # 3. Make Call
    print(f"\n{Colors.YELLOW}3. Testing Make Call{Colors.RESET}")
    print_result('/chat/make_call/', 'POST', 0, False, "Skipped - requires recipient ID")
    
    # 4. Join Call
    print(f"\n{Colors.YELLOW}4. Testing Join Call{Colors.RESET}")
    print_result('/chat/join_call/', 'POST', 0, False, "Skipped - requires call ID")
    
    # 5. Call History
    print(f"\n{Colors.YELLOW}5. Testing Call History{Colors.RESET}")
    success, status, data = test_endpoint(
        'GET', '/chat/call_history/',
        auth=True
    )
    print_result('/chat/call_history/', 'GET', status, success)
    
    # 6. Create Room
    print(f"\n{Colors.YELLOW}6. Testing Create Room{Colors.RESET}")
    print_result('/chat/create_room/', 'POST', 0, False, "Skipped - requires room data")
    
    # 7. Create Event
    print(f"\n{Colors.YELLOW}7. Testing Create Event{Colors.RESET}")
    print_result('/chat/create_event/', 'POST', 0, False, "Skipped - requires event data")
    
    # 8. Edit Event
    print(f"\n{Colors.YELLOW}8. Testing Edit Event{Colors.RESET}")
    print_result('/chat/edit_event/', 'PUT', 0, False, "Skipped - requires event ID")
    
    # 9. Event Detail
    print(f"\n{Colors.YELLOW}9. Testing Event Detail{Colors.RESET}")
    print_result('/chat/event_detail/', 'GET', 0, False, "Skipped - requires event ID")
    
    # 10. Add Member
    print(f"\n{Colors.YELLOW}10. Testing Add Member{Colors.RESET}")
    print_result('/chat/add_member/', 'POST', 0, False, "Skipped - requires event and user ID")
    
    # 11. Stop Event
    print(f"\n{Colors.YELLOW}11. Testing Stop Event{Colors.RESET}")
    print_result('/chat/stop_event/', 'POST', 0, False, "Skipped - requires event ID")
    
    # 12. Leave Event
    print(f"\n{Colors.YELLOW}12. Testing Leave Event{Colors.RESET}")
    print_result('/chat/leave_event/', 'POST', 0, False, "Skipped - requires event ID")
    
    # 13. Report Event
    print(f"\n{Colors.YELLOW}13. Testing Report Event{Colors.RESET}")
    print_result('/chat/report_event/', 'POST', 0, False, "Skipped - requires event ID")
    
    # 14. End Call
    print(f"\n{Colors.YELLOW}14. Testing End Call{Colors.RESET}")
    print_result('/chat/end_call/', 'POST', 0, False, "Skipped - requires call ID")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run all API tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔" + "═" * 78 + "╗")
    print("║" + "MISPEC BACKEND API COMPREHENSIVE TEST SUITE".center(78) + "║")
    print("║" + f"Base URL: {BASE_URL}".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print(Colors.RESET)
    
    print(f"\n{Colors.YELLOW}Note: Some tests are skipped as they require specific data or are destructive operations.{Colors.RESET}")
    print(f"{Colors.YELLOW}Update test_data dictionary with valid credentials to run full tests.{Colors.RESET}")
    
    # Run all test suites
    test_users_endpoints()
    test_profiles_endpoints()
    test_chat_endpoints()
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}")
    print("╔" + "═" * 78 + "╗")
    print("║" + "TEST SUITE COMPLETED".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print(Colors.RESET)


if __name__ == "__main__":
    main()
