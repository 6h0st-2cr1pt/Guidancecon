"""
Custom admin site configuration to restrict access to superusers only.
This ensures that sysadmin users (who have is_staff=True) cannot access Django admin.
"""
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin


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

