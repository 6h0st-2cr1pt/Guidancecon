from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, date, time
from .models import UserProfile, Appointment
from sysadmin.models import Timeslot


def home(request):
    return render(request, 'public/P_login.html')


def signup(request):
    if request.method == 'POST':
        # Get form data
        fname = request.POST.get('fname', '').strip()
        lname = request.POST.get('lname', '').strip()
        studentid = request.POST.get('studentid', '').strip()
        course = request.POST.get('course', '').strip()
        yearlevel = request.POST.get('yearlevel', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        # Keep form data for re-population
        context = {
            'fname': fname,
            'lname': lname,
            'studentid': studentid,
            'course': course,
            'yearlevel': yearlevel,
            'email': email
        }

        # Validate required fields
        if not all([studentid, email, password, confirm_password]):
            context['error'] = 'All fields are required.'
            return render(request, 'public/registration.html', context)

        if password != confirm_password:
            context['error'] = 'Passwords do not match.'
            return render(request, 'public/registration.html', context)

        # Check uniqueness
        if User.objects.filter(username=studentid).exists():
            context['error'] = 'An account with this Student ID already exists.'
            return render(request, 'public/registration.html', context)
        
        from .models import UserProfile
        if UserProfile.objects.filter(student_id=studentid).exists():
            context['error'] = 'This Student ID is already registered.'
            return render(request, 'public/registration.html', context)
        
        if User.objects.filter(email=email).exists():
            context['error'] = 'An account with this email already exists.'
            return render(request, 'public/registration.html', context)

        try:
            # Create user with student ID as username
            user = User.objects.create_user(
                username=studentid,
                email=email,
                password=password,
                first_name=fname,
                last_name=lname
            )

            # Create profile
            profile = UserProfile.objects.create(
                user=user,
                student_id=studentid,
                course=course,
                year_level=yearlevel
            )

            # Log the user in
            authenticated_user = authenticate(request, username=studentid, password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)
                return redirect('public:dashboard')
            else:
                print(f"Failed to authenticate user {studentid} after creation")
                context['error'] = 'Account created but login failed. Please try logging in.'
                return redirect('public:login')

        except Exception as e:
            import traceback
            print(f"Error creating user/profile: {str(e)}")
            print(traceback.format_exc())
            context['error'] = 'An error occurred during registration. Please try again.'
            return render(request, 'public/registration.html', context)

    return render(request, 'public/registration.html')


@login_required
def dashboard(request):
    # Simple dashboard that extends P_base and shows a welcome message
    return render(request, 'public/dashboard.html')


@login_required
def appointments(request):
    """Display appointment booking page with counselor selection and time slots"""
    counselors = User.objects.filter(is_staff=True, is_active=True)
    
    # Add counselor profile information
    counselors_with_profiles = []
    for counselor in counselors:
        counselor_data = {
            'id': counselor.id,
            'username': counselor.username,
            'name': counselor.get_full_name(),
            'title': '',
            'has_profile': False
        }
        
        # Try to get counselor profile
        try:
            from sysadmin.models import CounselorProfile
            profile = CounselorProfile.objects.get(user=counselor)
            counselor_data.update({
                'name': profile.get_full_name(),
                'title': profile.title,
                'has_profile': True
            })
        except CounselorProfile.DoesNotExist:
            pass
        
        counselors_with_profiles.append(counselor_data)
    
    context = {
        'counselors': counselors_with_profiles,
    }
    return render(request, 'public/appointment.html', context)


@login_required
def counselor_availability(request, counselor_id):
    """Display counselor availability for a specific date"""
    counselor = get_object_or_404(User, id=counselor_id, is_staff=True)
    
    # Parse the date parameter
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
    
    # Define only the 8 specific timeslots
    time_slots = [
        (8, '8:00 AM - 9:00 AM'),
        (9, '9:00 AM - 10:00 AM'),
        (10, '10:00 AM - 11:00 AM'),
        (11, '11:00 AM - 12:00 PM'),
        (13, '1:00 PM - 2:00 PM'),
        (14, '2:00 PM - 3:00 PM'),
        (15, '3:00 PM - 4:00 PM'),
        (16, '4:00 PM - 5:00 PM'),
    ]
    
    slots = []
    for hour, label in time_slots:
        slot_time = time(hour=hour, minute=0)
        ts, created = Timeslot.objects.get_or_create(
            user=counselor, 
            date=selected_date, 
            start_time=slot_time, 
            defaults={'available': False}
        )
        slots.append({
            'hour': hour,
            'label': label,
            'available': ts.available,
        })
    
    # Get counselor profile information
    counselor_info = {
        'id': counselor.id,
        'name': counselor.get_full_name(),
        'title': '',
        'bio': '',
        'profile_picture': None,
    }
    
    # Try to get counselor profile if it exists
    try:
        from sysadmin.models import CounselorProfile
        profile = CounselorProfile.objects.get(user=counselor)
        counselor_info.update({
            'name': profile.get_full_name(),
            'title': profile.title,
            'bio': profile.bio,
            'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
        })
    except CounselorProfile.DoesNotExist:
        pass
    
    return JsonResponse({
        'counselor': counselor_info['name'],
        'counselor_info': counselor_info,
        'date': selected_date.strftime('%Y-%m-%d'),
        'slots': slots,
    })


@login_required
def book_appointment(request):
    """Handle appointment booking"""
    if request.method == 'POST':
        timeslot_hour = request.POST.get('timeslot_id')  # This is now the hour (8, 9, 10, etc.)
        counselor_id = request.POST.get('counselor_id')
        program = request.POST.get('program', '')
        selected_date = request.POST.get('selected_date')
        
        try:
            counselor = get_object_or_404(User, id=counselor_id, is_staff=True)
            
            # Convert hour to time
            hour = int(timeslot_hour)
            start_time = time(hour, 0)
            
            # Get or create timeslot
            timeslot, created = Timeslot.objects.get_or_create(
                user=counselor,
                date=selected_date,
                start_time=start_time,
                defaults={'available': True}
            )
            
            # Check if timeslot is still available
            if not timeslot.available:
                messages.error(request, 'This time slot is no longer available.')
                return redirect('public:appointments')
            
            # Check if student already has an appointment at this time
            existing_appointment = Appointment.objects.filter(
                student=request.user,
                timeslot__date=timeslot.date,
                timeslot__start_time=timeslot.start_time,
                status__in=['pending', 'confirmed']
            ).exists()
            
            if existing_appointment:
                messages.error(request, 'You already have an appointment scheduled at this time.')
                return redirect('public:appointments')
            
            # Create appointment
            appointment = Appointment.objects.create(
                student=request.user,
                counselor=counselor,
                timeslot=timeslot,
                program=program,
                status='pending'
            )
            
            # Mark timeslot as unavailable
            timeslot.available = False
            timeslot.save()
            
            messages.success(request, 'Appointment booked successfully!')
            return redirect('public:my_appointments')
            
        except Exception as e:
            messages.error(request, f'Error booking appointment: {str(e)}')
            return redirect('public:appointments')
    
    return redirect('public:appointments')


@login_required
def my_appointments(request):
    """Display user's appointments (past and upcoming)"""
    now = timezone.now()
    today = now.date()
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        student=request.user,
        timeslot__date__gte=today,
        status__in=['pending', 'confirmed']
    ).order_by('timeslot__date', 'timeslot__start_time')
    
    # Get past appointments
    past_appointments = Appointment.objects.filter(
        student=request.user,
        timeslot__date__lt=today
    ).order_by('-timeslot__date', '-timeslot__start_time')
    
    context = {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
    }
    return render(request, 'public/my_appointments.html', context)


@login_required
def cancel_appointment(request, appointment_id):
    """Cancel an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, student=request.user)
    
    if appointment.status in ['pending', 'confirmed']:
        # Mark timeslot as available again
        appointment.timeslot.available = True
        appointment.timeslot.save()
        
        # Cancel appointment
        appointment.status = 'cancelled'
        appointment.save()
        
        messages.success(request, 'Appointment cancelled successfully.')
    else:
        messages.error(request, 'This appointment cannot be cancelled.')
    
    return redirect('public:my_appointments')


@login_required
def notifications(request):
    """Display notifications page"""
    return render(request, 'public/notifications.html')
