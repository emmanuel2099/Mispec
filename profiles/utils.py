import shortuuid
from decimal import Decimal
from geopy.distance import geodesic


def generate_referral_code():
    return shortuuid.ShortUUID().random(length=10)

def generate_uid_code():
    unique_id = shortuuid.ShortUUID().random(length=10)
    
    return hash(unique_id) % (10**9)


def calculate_distance(user_coords, target_coords):
    return geodesic(user_coords, target_coords).km
