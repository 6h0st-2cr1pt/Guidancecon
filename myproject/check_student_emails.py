"""
Check if students have email addresses
Run with: python manage.py shell < check_student_emails.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from public.models import Appointment

print("=" * 60)
print("Checking Student Email Addresses")
print("=" * 60)

# Get all students (non-staff users)
students = User.objects.filter(is_staff=False, is_active=True)

print(f"\nTotal students: {students.count()}")

students_with_email = 0
students_without_email = 0

print(f"\nStudent Email Status:")
for student in students:
    if student.email:
        students_with_email += 1
        print(f"  {student.username}: {student.email}")
    else:
        students_without_email += 1
        print(f"  {student.username}: NO EMAIL")

print(f"\nSummary:")
print(f"  Students with email: {students_with_email}")
print(f"  Students without email: {students_without_email}")

# Check recent appointments
print(f"\n" + "=" * 60)
print("Recent Appointments and Email Status")
print("=" * 60)

recent_appointments = Appointment.objects.select_related('student', 'counselor').order_by('-created_at')[:10]

if recent_appointments:
    print(f"\nLast 10 appointments:")
    for apt in recent_appointments:
        student_email = apt.student.email if apt.student.email else "NO EMAIL"
        status_icon = "✓" if apt.student.email else "✗"
        print(f"  {status_icon} Appointment ID {apt.id}: Student {apt.student.username} ({student_email}) - Status: {apt.status}")
else:
    print("No appointments found")

print(f"\n" + "=" * 60)
print("Recommendation:")
if students_without_email > 0:
    print(f"  {students_without_email} students don't have email addresses.")
    print(f"  These students won't receive appointment confirmation emails.")
    print(f"  Consider adding email addresses to student accounts.")
else:
    print(f"  All students have email addresses configured.")

