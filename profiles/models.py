from django.db import models
from users.models import CustomUser
import uuid
from decimal import Decimal
# from datetime import timezone
from django.utils import timezone



# Create your models here.

class Plan(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=200, blank=True, null=True)
    amount = models.PositiveIntegerField(default=0, blank=True, null=True)
    product_id = models.CharField(max_length=100, blank=True, null=True)
    duration = models.PositiveIntegerField(default=0, blank=True, null=True)
    max_minutes = models.PositiveIntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return self.name

class Gift(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='upload/gift', blank=True, null=True)
    price = models.PositiveIntegerField(default=0, blank=True, null=True)
    product_id = models.CharField(max_length=100, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.name
    

class Entertainment(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='upload/entertainment', blank=True, null=True)

    def __str__(self):
        return self.name
    
class Sport(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='upload/sport', blank=True, null=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    uid = models.IntegerField(blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)
    first_name = models.CharField(max_length=250, blank=True, null=True)
    last_name = models.CharField(max_length=250, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='upload/profile_picture', blank=True, null=True)
    profile_media = models.FileField(upload_to='upload/profile_media', blank=True, null=True)

    GENDER_CHOICES = [
        ('Male', 'male'),
        ('Female', 'female'),
    ]
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    ORIENTATION_CHOICES = [
        ('Male', 'male'),
        ('Female', 'female'),
        ('Both', 'both'),
    ]
    sexual_orientation = models.CharField(max_length=100, choices=ORIENTATION_CHOICES, blank=True, null=True)
    zodiac_sign = models.CharField(max_length=200, blank=True, null=True)
    entertainment = models.ManyToManyField(Entertainment, blank=True)
    sport = models.ManyToManyField(Sport, blank=True)
    why_are_you_here = models.CharField(max_length=200, blank=True, null=True)
    relationship_status = models.CharField(max_length=200, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=Decimal('0.0'), blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=Decimal('0.0'), blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, blank=True, null=True)
    referral_code = models.CharField(max_length=100, blank=True, null=True)
    occupation = models.CharField(max_length=200, blank=True, null=True)
    height = models.CharField(max_length=200, blank=True, null=True)
    fcm_token = models.CharField(max_length=250, blank=True, null=True)
    is_location = models.BooleanField(default=False, blank=True, null=True)
    is_incognito = models.BooleanField(default=False, blank=True, null=True)
    is_like_notification = models.BooleanField(default=True, blank=True, null=True)
    is_match_notification = models.BooleanField(default=True, blank=True, null=True)
    is_gift_notification = models.BooleanField(default=True, blank=True, null=True)
    is_chat_notification = models.BooleanField(default=True, blank=True, null=True)
    is_event_notification = models.BooleanField(default=True, blank=True, null=True)
    is_verified = models.BooleanField(default=False, blank=True, null=True)
    location_name = models.CharField(max_length=250, blank=True, null=True)
    distance = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.user.email
    
    def has_active_plan(self):
        return self.plan is not None
    
    def save(self, *args, **kwargs):
        if self.longitude == '':
            self.longitude = None
        if self.latitude == '':
            self.latitude = None
        super(Profile, self).save(*args, **kwargs)



class ProfileMedia(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='medias')
    files = models.FileField(upload_to='upload/profile_media', blank=True, null=True)
      
    def __str__(self):
        return f'{self.profile.first_name} {self.profile.last_name}'
    
class Like(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="sent_likes")
    receiver  = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="received_likes")
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.sender.email}  liked  {self.receiver.email}  profile"
    

class ProfileGift(models.Model):
    BOUGHT = 'bought'
    RECEIVED = 'received'
    TYPE_CHOICES = [
        (BOUGHT, 'Bought'),
        (RECEIVED, 'Received'),
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    gift = models.ForeignKey(Gift, on_delete=models.SET_NULL, blank=True, null=True)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="my_gifts")
    gift_type = models.CharField(max_length=100, choices=TYPE_CHOICES, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    is_reedemed = models.BooleanField(default=False, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.owner.email
    
    

class Block(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    blocked_by = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="blocks_sent")
    blocked_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="blocks_received")
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.blocked_by.email}  blocked  {self.blocked_user.email}  profile  at :  {self.timestamp}"

class Report(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    reported_by = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="reports_sent")
    reported_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="reports_received")
    reason = models.CharField(max_length=200, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.reported_by.email}  reported  {self.reported_user.email}  profile at :  {self.timestamp}"
    

class Referral(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    referred_by = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="referrals_sent")
    referred_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="referrals_received")
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    is_redeemed = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return f"{self.referred_by.email} -- referred -- {self.referred_user.email}"
    


class Match(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    profile_a = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user_profile_a')
    profile_b = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user_profile_b')
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Matches"
    def __str__(self):

        return f"{self.profile_a.email}  matches with  {self.profile_b.email}  profile"

NOTIFICATION_TYPES = [
        ('chat', 'Chat Notification'),
        ('like', 'Like Notification'),
        ('match', 'Match Notification'),
        ('gift', 'Gift Notification'),
        ('event', 'Event Notification'),
       
    ]

class Notification(models.Model):
    recipient = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    message = models.CharField(max_length=255, blank=True, null=True)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    is_read = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return f"{self.recipient} ---- {self.notification_type} ---- {self.is_read}"

    
class UserPlan(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, blank=True, null=True, db_index=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, blank=True, null=True, db_index=True)
    expiry_date = models.DateTimeField(db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    def __str__(self):
        return f"{self.profile} is on {self.plan.name} until {self.expiry_date}"

    def save(self, *args, **kwargs):
        if self.expiry_date and timezone.is_naive(self.expiry_date):
            self.expiry_date = timezone.make_aware(self.expiry_date, timezone.get_current_timezone())
        super(UserPlan, self).save(*args, **kwargs)

    def check_expiry(self):
        if self.expiry_date < timezone.now():
            self.is_active = False
            self.save()
            if self.profile:
                self.profile.plan = None
                self.profile.save()

   
    

class Support(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    sender = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f'{self.sender}  {self.timestamp}'
    