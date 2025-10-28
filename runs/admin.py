from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Run, SignUp, UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile to manage within User admin."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['phone_number', 'emergency_contact_name', 'emergency_contact_phone', 'date_of_birth']


class CustomUserAdmin(UserAdmin):
    """Extended User admin with UserProfile inline."""
    inlines = [UserProfileInline]


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class SignUpInline(admin.TabularInline):
    """Inline admin for SignUp to manage attendance within Run admin."""
    model = SignUp
    extra = 0
    fields = ['user', 'signed_up_at', 'attended']
    readonly_fields = ['signed_up_at']


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    """Admin interface for Run model."""
    list_display = ['venue', 'date', 'time', 'length_km', 'meeting_place', 'get_signups_count', 'max_capacity', 'is_full']
    list_filter = ['date', 'venue']
    search_fields = ['venue', 'meeting_place']
    inlines = [SignUpInline]
    
    def get_signups_count(self, obj):
        return obj.get_signups_count()
    get_signups_count.short_description = 'Sign-ups'
    
    def is_full(self, obj):
        return obj.is_full()
    is_full.boolean = True
    is_full.short_description = 'Full'


@admin.register(SignUp)
class SignUpAdmin(admin.ModelAdmin):
    """Admin interface for SignUp model."""
    list_display = ['user', 'run', 'signed_up_at', 'attended']
    list_filter = ['attended', 'run__date']
    search_fields = ['user__username', 'user__email', 'run__venue']
    readonly_fields = ['signed_up_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model."""
    list_display = ['user', 'emergency_contact_name', 'emergency_contact_phone', 'phone_number', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'emergency_contact_name', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'date_of_birth')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
