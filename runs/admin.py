from django.contrib import admin
from .models import Run, SignUp


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
