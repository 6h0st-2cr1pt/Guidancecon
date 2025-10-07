from django.db import models
from django.conf import settings
from django.utils import timezone


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

