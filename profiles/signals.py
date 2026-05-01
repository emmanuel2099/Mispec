from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomUser
from .models import Profile
from django.urls import reverse
from .utils import generate_referral_code, generate_uid_code




@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    user = instance
    if created:  
        profile = Profile.objects.create(
            user = user,
            email = user.email,
            first_name = user.first_name,
            last_name = user.last_name,
            referral_code = generate_referral_code(),
            uid = generate_uid_code()     
        )
        
            

@receiver(post_save, sender=Profile)
def update_user(sender, instance, created, **kwargs):
    profile = instance
    user = profile.user

    if created == False:
        user.first_name = profile.first_name
        user.last_name = profile.last_name
        user.save()


