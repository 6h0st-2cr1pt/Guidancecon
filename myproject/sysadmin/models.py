from django.db import models
from django.conf import settings
from django.utils import timezone


# Counselor profile model for additional information
class CounselorProfile(models.Model):
    """Extended profile information for counselors"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='counselor_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=10, blank=True)
    title = models.CharField(max_length=100, blank=True, help_text="e.g., PhD, RGC, LPT")
    profile_picture = models.ImageField(upload_to='counselor_profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, help_text="Brief description about the counselor")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.title}"

    def get_full_name(self):
        if self.middle_initial:
            return f"{self.first_name} {self.middle_initial}. {self.last_name}"
        return f"{self.first_name} {self.last_name}"


# Simple timeslot model for availability
class Timeslot(models.Model):
	"""Represents a 1-hour timeslot on a given date for a user (counselor).

	The UI will show timeslots from 8:00 to 17:00 (5 PM). Availability is a boolean.
	"""
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='timeslots')
	date = models.DateField()
	start_time = models.TimeField()
	available = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = (('user', 'date', 'start_time'),)
		ordering = ('date', 'start_time')

	def __str__(self):
		return f"{self.user} - {self.date} {self.start_time} - {'Available' if self.available else 'Not Available'}"

