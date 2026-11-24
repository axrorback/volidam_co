from django.contrib import admin
from .models import CustomUser , SMSLog , OTPVerification
from django.contrib.auth.admin import UserAdmin



@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('phone', 'full_name', 'is_phone_verified', 'role', 'created_at')
    ordering = ('-created_at',)  # yoki ('phone',)
    search_fields = ('phone', 'full_name')

    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal info', {'fields': ('full_name', 'role', 'is_phone_verified')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'full_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('phone','created_at',)


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('phone','otp_hash','created_at','is_expired')


