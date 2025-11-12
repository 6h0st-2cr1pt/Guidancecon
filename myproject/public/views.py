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


def about(request):
    return render(request, 'public/about.html')


def signup(request):
    if request.method == 'POST':
        # Get form data
        fname = request.POST.get('fname', '').strip()
        lname = request.POST.get('lname', '').strip()
        studentid = request.POST.get('studentid', '').strip()
        college = request.POST.get('college', '').strip()
        course = request.POST.get('course', '').strip()
        yearlevel = request.POST.get('yearlevel', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        profile_picture = request.FILES.get('profile_picture')
        gender = request.POST.get('gender', '').strip()
        age = request.POST.get('age', '').strip()
        gender = request.POST.get('gender', '').strip()
        age = request.POST.get('age', '').strip()

        # Keep form data for re-population
        context = {
            'fname': fname,
            'lname': lname,
            'studentid': studentid,
            'college': college,
            'course': course,
            'yearlevel': yearlevel,
            'email': email,
            'gender': gender,
            'age': age
        }

        # Validate required fields
        if not all([studentid, college, course, email, password, confirm_password, gender, age]):
            context['error'] = 'All fields are required.'
            return render(request, 'public/registration.html', context)

        # Validate age is a number in range
        try:
            age_int = int(age)
            if age_int < 12 or age_int > 120:
                raise ValueError()
        except ValueError:
            context['error'] = 'Please enter a valid age (12-120).'
            return render(request, 'public/registration.html', context)

        if password != confirm_password:
            context['error'] = 'Passwords do not match.'
            return render(request, 'public/registration.html', context)

        # Validate terms acceptance
        terms_accepted = request.POST.get('terms_accepted')
        if not terms_accepted:
            context['error'] = 'You must agree to the Terms of Services and Privacy Policy to continue.'
            return render(request, 'public/registration.html', context)

        # Validate profile picture size (2 MB limit)
        if profile_picture:
            max_size = 2 * 1024 * 1024  # 2 MB in bytes
            if profile_picture.size > max_size:
                size_mb = profile_picture.size / (1024 * 1024)
                context['error'] = f'Profile picture is too large ({size_mb:.2f} MB). Maximum allowed size is 2 MB.'
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

            # Process profile picture if uploaded
            if profile_picture:
                image_binary = profile_picture.read()
                from django.db import connection
                from psycopg2 import Binary
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE auth_user SET image_data = %s WHERE id = %s",
                        [Binary(image_binary), user.id]
            )

            # Create profile
            profile = UserProfile.objects.create(
                user=user,
                student_id=studentid,
                college=college,
                course=course,
                year_level=yearlevel,
                gender=gender,
                age=age_int
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
    # Get student's college from their profile
    try:
        student_profile = UserProfile.objects.get(user=request.user)
        student_college = student_profile.college
    except UserProfile.DoesNotExist:
        student_college = None
    
    counselors = User.objects.filter(is_staff=True, is_active=True)
    
    # Add counselor information from User model using raw SQL and filter by college
    from django.db import connection
    counselors_with_profiles = []
    for counselor in counselors:
        with connection.cursor() as cursor:
            cursor.execute("SELECT middle_initial, assigned_college, title, bio FROM auth_user WHERE id = %s", [counselor.id])
            row = cursor.fetchone()
            middle_initial = row[0] if row[0] else ''
            assigned_college = row[1] if row[1] else ''
            title = row[2] if row[2] else ''
            bio = row[3] if row[3] else ''
        
        # Filter counselors by college:
        # - Only show counselors who have an assigned_college set
        # - If student has a college, show only counselors with matching assigned_college
        # - If student has no college, show all counselors with assigned_college
        # - Exclude counselors without assigned_college (empty/null)
        if not assigned_college or not assigned_college.strip():
            # Skip counselors without assigned_college
            continue
        
        if student_college:
            # Student has a college - only show counselors with matching assigned_college
            if assigned_college.strip() != student_college:
                continue
        
        # Helper function to get full name with middle initial
        def get_full_name_with_mi(user, mi):
            if mi:
                return f"{user.first_name} {mi}. {user.last_name}"
            return f"{user.first_name} {user.last_name}"
        
        counselor_data = {
            'id': counselor.id,
            'username': counselor.username,
            'name': get_full_name_with_mi(counselor, middle_initial),
            'title': title,
            'assigned_college': assigned_college,
            'has_profile': bool(title or bio)
        }
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
    
    # Get counselor information from User model using raw SQL
    from django.db import connection
    from django.urls import reverse
    with connection.cursor() as cursor:
        cursor.execute("SELECT middle_initial, assigned_college, title, bio, image_data FROM auth_user WHERE id = %s", [counselor.id])
        row = cursor.fetchone()
        middle_initial = row[0] if row[0] else ''
        assigned_college = row[1] if row[1] else ''
        title = row[2] if row[2] else ''
        bio = row[3] if row[3] else ''
        has_image = row[4] is not None
    
    # Helper function to get full name with middle initial
    def get_full_name_with_mi(user, mi):
        if mi:
            return f"{user.first_name} {mi}. {user.last_name}"
        return f"{user.first_name} {user.last_name}"
    
    # Generate profile picture URL if image exists
    profile_picture_url = None
    if has_image:
        profile_picture_url = reverse('public:profile_picture', args=[counselor.id])
    
    counselor_info = {
        'id': counselor.id,
        'name': get_full_name_with_mi(counselor, middle_initial),
        'title': title,
        'bio': bio,
        'profile_picture': profile_picture_url,
    }
    
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
        selected_date = request.POST.get('selected_date')
        
        # Get program from user's profile
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            program = user_profile.course  # Using 'course' field to store program
        except UserProfile.DoesNotExist:
            program = 'Not Specified'
        
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
            
            # Send email notification to student
            from .utils import send_appointment_confirmation_email, create_counselor_notification
            email_sent = send_appointment_confirmation_email(request.user, appointment)
            
            # Create notification for counselor
            notification_created = create_counselor_notification(counselor, appointment, 'appointment_booked')
            
            # Always show success message regardless of email status
            messages.success(request, 'Appointment booked successfully! Check your appointments page.')
            
            return redirect('public:my_appointments')
            
        except Exception as e:
            messages.error(request, f'Error booking appointment: {str(e)}')
            return redirect('public:appointments')
    
    return redirect('public:appointments')


@login_required
def my_appointments(request):
    """Display user's appointments (past and upcoming)"""
    from django.db import connection
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
    
    # Fetch counselor titles for all appointments
    def add_counselor_info(appointments):
        appointments_with_info = []
        for appointment in appointments:
            with connection.cursor() as cursor:
                cursor.execute("SELECT title FROM auth_user WHERE id = %s", [appointment.counselor.id])
                row = cursor.fetchone()
                appointment.counselor_title = row[0] if row and row[0] else 'Guidance Counselor'
            appointments_with_info.append(appointment)
        return appointments_with_info
    
    context = {
        'upcoming_appointments': add_counselor_info(list(upcoming_appointments)),
        'past_appointments': add_counselor_info(list(past_appointments)),
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
            
            # Create notification for counselor about cancellation
            from .utils import create_counselor_notification
            create_counselor_notification(appointment.counselor, appointment, 'appointment_cancelled')
            
            messages.success(request, 'Appointment cancelled successfully.')
    else:
        messages.error(request, 'This appointment cannot be cancelled.')
    
    return redirect('public:my_appointments')


@login_required
def notifications(request):
    """Display notifications page"""
    from django.db import connection
    from datetime import timedelta
    
    # Get all appointments for the student
    appointments = Appointment.objects.filter(student=request.user).order_by('-created_at')[:20]
    
    # Create notification-like data from appointments
    notifications_list = []
    for appointment in appointments:
        # Fetch counselor info
        with connection.cursor() as cursor:
            cursor.execute("SELECT title FROM auth_user WHERE id = %s", [appointment.counselor.id])
            row = cursor.fetchone()
            counselor_title = row[0] if row and row[0] else 'Guidance Counselor'
        
        counselor_name = appointment.counselor.get_full_name() or appointment.counselor.username
        
        # Create notification based on appointment status
        if appointment.status == 'confirmed':
            notifications_list.append({
                'icon': '✅',
                'title': 'Appointment Confirmed',
                'message': f'Your appointment with {counselor_name} ({counselor_title}) has been confirmed for {appointment.timeslot.date.strftime("%B %d, %Y")} at {appointment.timeslot.start_time.strftime("%I:%M %p")}.',
                'time_ago': get_time_ago(appointment.updated_at),
                'is_unread': (timezone.now() - appointment.updated_at).days < 1,
                'created_at': appointment.updated_at,
            })
        elif appointment.status == 'pending':
            notifications_list.append({
                'icon': '⏳',
                'title': 'Appointment Pending',
                'message': f'Your appointment request with {counselor_name} ({counselor_title}) for {appointment.timeslot.date.strftime("%B %d, %Y")} at {appointment.timeslot.start_time.strftime("%I:%M %p")} is awaiting confirmation.',
                'time_ago': get_time_ago(appointment.created_at),
                'is_unread': (timezone.now() - appointment.created_at).days < 1,
                'created_at': appointment.created_at,
            })
        elif appointment.status == 'cancelled':
            notifications_list.append({
                'icon': '❌',
                'title': 'Appointment Cancelled',
                'message': f'Your appointment with {counselor_name} ({counselor_title}) scheduled for {appointment.timeslot.date.strftime("%B %d, %Y")} at {appointment.timeslot.start_time.strftime("%I:%M %p")} has been cancelled.',
                'time_ago': get_time_ago(appointment.updated_at),
                'is_unread': (timezone.now() - appointment.updated_at).days < 1,
                'created_at': appointment.updated_at,
            })
        elif appointment.status == 'completed':
            notifications_list.append({
                'icon': '🎉',
                'title': 'Appointment Completed',
                'message': f'Your counseling session with {counselor_name} ({counselor_title}) has been completed. Thank you for using our services.',
                'time_ago': get_time_ago(appointment.updated_at),
                'is_unread': False,
                'created_at': appointment.updated_at,
            })
    
    context = {
        'notifications': notifications_list,
    }
    return render(request, 'public/notifications.html', context)


def get_time_ago(dt):
    """Convert datetime to human-readable time ago format"""
    now = timezone.now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"


def profile_picture(request, user_id):
    """Serve profile picture from database"""
    from django.db import connection
    from django.http import HttpResponse, HttpResponseNotFound
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT image_data FROM auth_user WHERE id = %s", [user_id])
        row = cursor.fetchone()
        
        if row and row[0]:
            image_data = bytes(row[0])
            # Try to determine content type from image data
            content_type = 'image/jpeg'  # default
            if image_data.startswith(b'\x89PNG'):
                content_type = 'image/png'
            elif image_data.startswith(b'GIF'):
                content_type = 'image/gif'
            elif image_data.startswith(b'\xff\xd8\xff'):
                content_type = 'image/jpeg'
            
            response = HttpResponse(image_data, content_type=content_type)
            response['Cache-Control'] = 'public, max-age=86400'  # Cache for 1 day
            return response
    
    # Return a default placeholder image or 404
    return HttpResponseNotFound('No profile picture found')


@login_required
def profile(request):
    """Manage student profile"""
    # Get student's profile
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profile not found. Please contact administrator.')
        return redirect('public:dashboard')
    
    if request.method == 'POST':
        # Get form data
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        student_id = request.POST.get('student_id', '').strip()
        college = request.POST.get('college', '').strip()
        course = request.POST.get('course', '').strip()
        year_level = request.POST.get('year_level', '').strip()
        gender = request.POST.get('gender', '').strip()
        age = request.POST.get('age', '').strip()
        profile_picture = request.FILES.get('profile_picture')
        current_password = request.POST.get('current_password', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        context = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'student_id': student_id,
            'college': college,
            'course': course,
            'year_level': year_level,
            'gender': gender,
            'age': age,
        }
        
        # Validation
        if not all([email, first_name, last_name, student_id, college, course, gender, age]):
            context['error'] = 'Email, name, student ID, college, and course are required.'
            return render(request, 'public/profile.html', context)

        # Validate age
        try:
            age_int = int(age)
            if age_int < 12 or age_int > 120:
                raise ValueError()
        except ValueError:
            context['error'] = 'Please enter a valid age (12-120).'
            return render(request, 'public/profile.html', context)
        
        # Check if email is taken by another user
        if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            context['error'] = 'This email is already taken by another user.'
            return render(request, 'public/profile.html', context)
        
        # Check if student ID is taken by another user
        if UserProfile.objects.filter(student_id=student_id).exclude(user=request.user).exists():
            context['error'] = 'This student ID is already taken by another user.'
            return render(request, 'public/profile.html', context)
        
        # Validate profile picture size (2 MB limit)
        if profile_picture:
            max_size = 2 * 1024 * 1024  # 2 MB in bytes
            if profile_picture.size > max_size:
                size_mb = profile_picture.size / (1024 * 1024)
                context['error'] = f'Profile picture is too large ({size_mb:.2f} MB). Maximum allowed size is 2 MB.'
                return render(request, 'public/profile.html', context)
        
        # Handle password change
        if new_password or confirm_password:
            if not current_password:
                context['error'] = 'Current password is required to change password.'
                return render(request, 'public/profile.html', context)
            
            if not request.user.check_password(current_password):
                context['error'] = 'Current password is incorrect.'
                return render(request, 'public/profile.html', context)
            
            if new_password != confirm_password:
                context['error'] = 'New passwords do not match.'
                return render(request, 'public/profile.html', context)
            
            if len(new_password) < 6:
                context['error'] = 'New password must be at least 6 characters long.'
                return render(request, 'public/profile.html', context)
        
        try:
            # Update user information
            user = request.user
            user.email = email
            # Note: username should stay as student_id, don't change it
            user.first_name = first_name
            user.last_name = last_name
            
            # Update password if provided
            if new_password:
                user.set_password(new_password)
            
            user.save()
            
            # Process profile picture if uploaded
            if profile_picture:
                image_binary = profile_picture.read()
                from django.db import connection
                from psycopg2 import Binary
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE auth_user SET image_data = %s WHERE id = %s",
                        [Binary(image_binary), user.id]
                    )
            
            # Update profile information
            user_profile.student_id = student_id
            user_profile.college = college
            user_profile.course = course
            user_profile.year_level = year_level
            user_profile.gender = gender
            user_profile.age = age_int
            user_profile.save()
            
            messages.success(request, 'Profile updated successfully!')
            
            # If password was changed, re-authenticate
            if new_password:
                user = authenticate(request, username=user.username, password=new_password)
                if user:
                    login(request, user)
            
            return redirect('public:profile')
            
        except Exception as e:
            context['error'] = f'Error updating profile: {str(e)}'
            return render(request, 'public/profile.html', context)
    
    # GET request - display form with current data
    context = {
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'student_id': user_profile.student_id,
        'college': user_profile.college,
        'course': user_profile.course,
        'year_level': user_profile.year_level,
        'gender': user_profile.gender,
        'age': user_profile.age,
    }
    return render(request, 'public/profile.html', context)
