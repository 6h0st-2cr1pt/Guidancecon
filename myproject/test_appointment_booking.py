"""
Test script to verify appointment booking logic
Run this with: python manage.py shell < test_appointment_booking.py
Or: python manage.py shell, then copy-paste this code
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model
from public.models import Appointment, UserProfile
from sysadmin.models import Timeslot
from django.db import transaction
from datetime import date, time

User = get_user_model()

print("=" * 60)
print("Testing Appointment Booking Logic")
print("=" * 60)

# Get or create test users
try:
    student = User.objects.filter(is_staff=False).first()
    if not student:
        print("❌ No student user found. Please create a student user first.")
        exit(1)
    print(f"✅ Using student: {student.username} (ID: {student.id})")
except Exception as e:
    print(f"❌ Error getting student: {e}")
    exit(1)

try:
    counselor = User.objects.filter(is_staff=True).first()
    if not counselor:
        print("❌ No counselor user found. Please create a counselor user first.")
        exit(1)
    print(f"✅ Using counselor: {counselor.username} (ID: {counselor.id})")
except Exception as e:
    print(f"❌ Error getting counselor: {e}")
    exit(1)

# Get program from user profile
try:
    user_profile = UserProfile.objects.get(user=student)
    program = user_profile.course or 'Not Specified'
    print(f"✅ Program: {program}")
except UserProfile.DoesNotExist:
    program = 'Not Specified'
    print(f"⚠️ No profile found, using default program: {program}")

# Create test timeslot
test_date = date.today()
test_time = time(14, 0)  # 2:00 PM

print(f"\n📅 Creating test timeslot: {test_date} at {test_time}")

try:
    timeslot, created = Timeslot.objects.get_or_create(
        user=counselor,
        date=test_date,
        start_time=test_time,
        defaults={'available': True}
    )
    print(f"✅ Timeslot {'created' if created else 'retrieved'}: ID={timeslot.id}, Available={timeslot.available}")
    
    # Reset availability if needed
    timeslot_taken = Appointment.objects.filter(
        timeslot=timeslot,
        status__in=['pending', 'confirmed']
    ).exists()
    
    if not timeslot_taken and not timeslot.available:
        print(f"ℹ️ Resetting timeslot availability")
        timeslot.available = True
        timeslot.save()
    
    if not timeslot.available:
        print(f"⚠️ Timeslot is not available, but continuing test...")
        timeslot.available = True
        timeslot.save()
        
except Exception as e:
    print(f"❌ Error creating timeslot: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test appointment creation
print(f"\n📝 Creating appointment...")
appointment = None
appointment_id = None

try:
    with transaction.atomic():
        # Create appointment
        appointment = Appointment.objects.create(
            student=student,
            counselor=counselor,
            timeslot=timeslot,
            program=program,
            status='pending'
        )
        appointment_id = appointment.id
        print(f"✅ Appointment CREATED in transaction: ID={appointment_id}")
        print(f"   Student: {appointment.student.username}")
        print(f"   Counselor: {appointment.counselor.username}")
        print(f"   Status: {appointment.status}")
        print(f"   Timeslot: {appointment.timeslot.id if appointment.timeslot else 'None'}")
        
        # Mark timeslot as unavailable
        timeslot.available = False
        timeslot.save(update_fields=['available'])
        print(f"✅ Timeslot {timeslot.id} marked as unavailable")
    
    # Verify after transaction commit
    print(f"\n🔍 Verifying appointment after transaction commit...")
    verify_appointment = Appointment.objects.filter(id=appointment_id).first()
    
    if not verify_appointment:
        print(f"❌ CRITICAL: Appointment {appointment_id} NOT found after commit!")
        exit(1)
    
    print(f"✅ Appointment VERIFIED: ID={verify_appointment.id}")
    print(f"   Student: {verify_appointment.student.username}")
    print(f"   Counselor: {verify_appointment.counselor.username}")
    print(f"   Status: {verify_appointment.status}")
    print(f"   Program: {verify_appointment.program}")
    print(f"   Created: {verify_appointment.created_at}")
    
    # Final check - query directly
    final_check = Appointment.objects.get(id=appointment_id)
    print(f"✅ Final check passed: Appointment {appointment_id} exists in database")
    
    # Count total appointments
    total_appointments = Appointment.objects.count()
    print(f"\n📊 Total appointments in database: {total_appointments}")
    
    print(f"\n✅ TEST PASSED: Appointment was successfully saved to database!")
    print(f"   Appointment ID: {appointment_id}")
    print(f"\n💡 You can now delete this test appointment if needed:")
    print(f"   Appointment.objects.get(id={appointment_id}).delete()")
    
except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

