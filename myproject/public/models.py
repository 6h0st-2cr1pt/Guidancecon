from django.db import models
from django.conf import settings


# Profile for public users (students)
class UserProfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
	student_id = models.CharField(max_length=50, unique=True)
	course = models.CharField(max_length=255, blank=True)
	year_level = models.CharField(max_length=50, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Profile for {self.user.username}"


# Appointment model for booking sessions
class Appointment(models.Model):
	STATUS_CHOICES = [
		('pending', 'Pending'),
		('confirmed', 'Confirmed'),
		('cancelled', 'Cancelled'),
		('completed', 'Completed'),
	]
	
	student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_appointments')
	counselor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='counselor_appointments')
	timeslot = models.ForeignKey('sysadmin.Timeslot', on_delete=models.CASCADE, related_name='appointments', null=True, blank=True, db_column='timeslot_id')
	program = models.CharField(max_length=255, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		if self.timeslot:
			return f"{self.student.get_full_name()} - {self.counselor.get_full_name()} on {self.timeslot.date} at {self.timeslot.start_time}"
		return f"{self.student.get_full_name()} - {self.counselor.get_full_name()}"
