from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, OtpCheck

# Register your models here.




class CustomUserAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    list_display = ('email', 'phone_number', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'created_at')
    
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'provider', 'provider_id', 'referral_code')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('created_at',)  # Make 'created_at' a read-only field

    search_fields = ('email', 'phone_number')
    ordering = ('email',)
    filter_horizontal = ()

# Register the new UserAdmin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(OtpCheck)
