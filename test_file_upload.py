"""
Test profile picture and media upload via PUT /profiles/profiles_update/
"""
import requests
import time
import io
from PIL import Image

BASE_URL = "https://mispec.onrender.com"
RUN_ID = str(int(time.time()))[-6:]
TEST_EMAIL = f"uploadtest_{RUN_ID}@example.com"
TEST_PHONE = f"+23481{RUN_ID}"
TEST_PASSWORD = "Test1234!"


def make_test_image(name="test.jpg"):
    """Create a minimal in-memory JPEG image."""
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return (name, buf, "image/jpeg")


def setup():
    # Send OTP
    r = requests.post(f"{BASE_URL}/users/send_otp/", json={"email": TEST_EMAIL, "phone_number": TEST_PHONE})
    if r.status_code != 200:
        print(f"❌ send_otp failed: {r.status_code} {r.text[:300]}")
        return None
    otp = r.json().get("otp")
    print(f"  OTP: {otp}")

    # Register
    r = requests.post(f"{BASE_URL}/users/register/", json={
        "email": TEST_EMAIL, "phone_number": TEST_PHONE,
        "otp": otp, "password": TEST_PASSWORD
    })
    if r.status_code not in (200, 201):
        print(f"❌ register failed: {r.status_code} {r.text[:300]}")
        return None

    token = r.json().get("tokens", {}).get("access")
    print(f"  Registered as {TEST_EMAIL}")
    return token


def get_user_id(token):
    r = requests.get(
        f"{BASE_URL}/profiles/profiles_update/",
        headers={"Authorization": f"Bearer {token}"}
    )
    if r.status_code == 200:
        return r.json().get("user")
    return None


def test_profile_picture_upload(token, user_id):
    print("\n--- Test: profile_picture upload ---")
    files = {"profile_picture": make_test_image("profile.jpg")}
    data = {"user": user_id, "first_name": "Upload", "last_name": "Test"}
    r = requests.put(
        f"{BASE_URL}/profiles/profiles_update/",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
        data=data,
    )
    print(f"  Status: {r.status_code}")
    try:
        body = r.json()
        pic = body.get("profile_picture")
        print(f"  profile_picture URL: {pic}")
        if r.status_code == 200 and pic and pic.startswith("http"):
            print("  ✅ PASS — profile picture uploaded to Cloudinary")
        else:
            print(f"  ❌ FAIL — {body}")
    except Exception:
        print(f"  ❌ FAIL — non-JSON response: {r.text[:400]}")


def test_media_upload(token, user_id):
    print("\n--- Test: uploaded_medias upload ---")
    files = [
        ("uploaded_medias", make_test_image("media1.jpg")),
        ("uploaded_medias", make_test_image("media2.jpg")),
    ]
    data = {"user": user_id}
    r = requests.put(
        f"{BASE_URL}/profiles/profiles_update/",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
        data=data,
    )
    print(f"  Status: {r.status_code}")
    try:
        body = r.json()
        medias = body.get("medias", [])
        print(f"  medias count: {len(medias)}")
        if r.status_code == 200 and medias:
            print(f"  ✅ PASS — {len(medias)} media file(s) uploaded")
        else:
            print(f"  ❌ FAIL — {body}")
    except Exception:
        print(f"  ❌ FAIL — non-JSON response: {r.text[:400]}")


if __name__ == "__main__":
    print(f"Testing file upload at {BASE_URL}\n" + "-"*50)
    token = setup()
    if not token:
        exit(1)

    user_id = get_user_id(token)
    print(f"  user_id: {user_id}")

    test_profile_picture_upload(token, user_id)
    test_media_upload(token, user_id)
