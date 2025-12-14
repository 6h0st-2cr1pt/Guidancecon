"""
Custom admin site configuration to restrict access to superusers only.
This ensures that sysadmin users (who have is_staff=True) cannot access Django admin.
"""
from django.contrib.admin import AdminSite, ModelAdmin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

# Import models from public and sysadmin apps
from public.models import UserProfile, Appointment
from sysadmin.models import Timeslot, Notification


class SuperuserOnlyAdminSite(AdminSite):
    """
    Custom admin site that only allows superusers to access it.
    This prevents sysadmin users (who have is_staff=True) from accessing Django admin.
    """
    
    def has_permission(self, request):
        """
        Only allow superusers to access the admin site.
        Regular staff users (like sysadmin counselors) will be denied access.
        """
        return (
            request.user and
            request.user.is_active and
            request.user.is_superuser
        )


# Create custom admin site instance
admin_site = SuperuserOnlyAdminSite(name='admin')

# Register default admin models with our custom site
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)


# Admin classes for Public app models
class UserProfileAdmin(ModelAdmin):
    list_display = ('user', 'student_id', 'college', 'course', 'year_level', 'gender', 'age', 'created_at')
    list_filter = ('college', 'course', 'year_level', 'gender', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'student_id', 'college', 'course')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


class AppointmentAdmin(ModelAdmin):
    list_display = ('id', 'student', 'counselor', 'timeslot', 'status', 'program', 'created_at')
    list_filter = ('status', 'created_at', 'counselor', 'student')
    search_fields = ('student__username', 'student__email', 'student__first_name', 'student__last_name',
                     'counselor__username', 'counselor__email', 'counselor__first_name', 'counselor__last_name',
                     'program')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'


# Admin classes for Sysadmin app models
class TimeslotAdmin(ModelAdmin):
    list_display = ('id', 'user', 'date', 'start_time', 'available', 'created_at')
    list_filter = ('available', 'date', 'created_at', 'user')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-date', 'start_time')
    date_hierarchy = 'date'


class NotificationAdmin(ModelAdmin):
    list_display = ('id', 'counselor', 'title', 'notification_type', 'is_read', 'created_at', 'appointment')
    list_filter = ('notification_type', 'is_read', 'created_at', 'counselor')
    search_fields = ('counselor__username', 'counselor__email', 'counselor__first_name', 'counselor__last_name',
                     'title', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_editable = ('is_read',)  # Allow quick editing of read status


# Register all models with the admin site
admin_site.register(UserProfile, UserProfileAdmin)
admin_site.register(Appointment, AppointmentAdmin)
admin_site.register(Timeslot, TimeslotAdmin)
admin_site.register(Notification, NotificationAdmin)

