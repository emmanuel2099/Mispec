from celery import shared_task
from .models import UserPlan, Profile
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
from geopy.geocoders import Nominatim


@shared_task
def check_user_plans():
    print("Starting task to check user plans")
    now = timezone.now()

    with transaction.atomic():
        expired_plans = UserPlan.objects.filter(is_active=True, expiry_date__lt=now)
        
        profile_ids_to_update = list(expired_plans.values_list('profile_id', flat=True))
        
        # Step 2: Deactivate expired plans in bulk
        expired_plans.update(is_active=False)
        
        # Step 3: Update profiles to set plan to None
        profiles_updated = Profile.objects.filter(id__in=profile_ids_to_update).update(plan=None)

    print(f"Deactivated {expired_plans.count()} plans and updated {profiles_updated} profiles to set plan to None")



@shared_task
def process_geocoding(profile_id, latitude, longitude):
    geolocator = Nominatim(user_agent="profile_locator")
    cache_key = f"geocode_{latitude}_{longitude}"

    # Check if the result is already cached
    cached_location = cache.get(cache_key)

    if not cached_location:
        location = geolocator.reverse((latitude, longitude), language="en")
        location_address = location.address if location else None

        # Cache the location result
        cache.set(cache_key, location_address, timeout=86400)  # Cache for 1 day

    # Update the profile with the location
    Profile.objects.filter(id=profile_id).update(location_name=cached_location)




    # def check_user_plans():
#     logger.info("starting task")
#     now = timezone.now()
#     expired_plans = UserPlan.objects.filter(is_active=True, expiry_date__lt=now)
#     for user_plan in expired_plans:
#         user_plan.is_active = False
#         user_plan.save()
#         user_plan.profile.plan = None  # Revert to free plan
#         user_plan.profile.save()
    # logger.info("task working fine")
