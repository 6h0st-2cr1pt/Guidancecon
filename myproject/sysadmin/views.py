from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.contrib import messages
from datetime import date, time, datetime, timedelta
from django.utils import timezone

from .models import Timeslot, Notification
from public.models import Appointment

@login_required
def dashboard(request):
    # Get recent notifications for the counselor
    notifications = Notification.objects.filter(counselor=request.user).order_by('-created_at')[:5]
    unread_count = Notification.objects.filter(counselor=request.user, is_read=False).count()
    
    # Get current date for filtering
    today = timezone.now().date()
    
    # Get upcoming appointments (today and future)
    upcoming_appointments = Appointment.objects.filter(
        counselor=request.user,
        timeslot__date__gte=today,
        status__in=['pending', 'confirmed']
    ).order_by('timeslot__date', 'timeslot__start_time')
    
    # Get past appointments (before today)
    past_appointments = Appointment.objects.filter(
        counselor=request.user,
        timeslot__date__lt=today
    ).order_by('-timeslot__date', '-timeslot__start_time')
    
    # Get today's appointments for quick overview
    today_appointments = Appointment.objects.filter(
        counselor=request.user,
        timeslot__date=today,
        status__in=['pending', 'confirmed']
    ).order_by('timeslot__start_time')

    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'today_appointments': today_appointments,
        'today': today,
    }
    return render(request, 'sysadmin/dashboard.html', context)


def index(request):
    return redirect('sysadmin:login')


def about(request):
    return render(request, 'sysadmin/about.html')


def login_view(request):
    """Custom login view for sysadmin that ensures is_staff=True"""
    from django.contrib.auth.views import LoginView as BaseLoginView
    from django.contrib.auth import login as auth_login
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Ensure user is staff when logging in through sysadmin
            if not user.is_staff:
                user.is_staff = True
                user.save()
            auth_login(request, user)
            next_url = request.GET.get('next', 'sysadmin:dashboard')
            return redirect(next_url)
        else:
            from django.contrib import messages
            messages.error(request, 'Invalid credentials. Please try again.')
    
    return render(request, 'sysadmin/login.html', {'form': None})


@login_required
def availability(request):
    # Accept a date parameter (YYYY-MM-DD) or default to today
    date_str = request.GET.get('date')
    try:
        if date_str:
            the_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            the_date = date.today()
    except Exception:
        the_date = date.today()

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
    user = request.user

    for hour, label in time_slots:
        slot_time = time(hour=hour, minute=0)
        ts, created = Timeslot.objects.get_or_create(
            user=user, 
            date=the_date, 
            start_time=slot_time, 
            defaults={'available': False}
        )
        slots.append({
            'id': ts.id,
            'hour': hour,
            'label': label,
            'available': ts.available,
        })

    # Get availability summary for next 7 days
    from datetime import timedelta
    summary_dates = []
    for i in range(7):
        summary_date = the_date + timedelta(days=i)
        date_slots = Timeslot.objects.filter(user=user, date=summary_date)
        available_count = date_slots.filter(available=True).count()
        summary_dates.append({
            'date': summary_date,
            'date_str': summary_date.strftime('%Y-%m-%d'),
            'available_count': available_count,
            'total_slots': 8,
        })

    context = {
        'slots': slots,
        'date': the_date,
        'date_str': the_date.strftime('%Y-%m-%d'),
        'summary_dates': summary_dates,
    }
    return render(request, 'sysadmin/availability.html', context)


@login_required
@require_POST
def toggle_availability(request):
    # Expect JSON or form with date and hour
    slot_id = request.POST.get('slot_id') or request.POST.get('id')
    if not slot_id:
        return HttpResponseBadRequest('Missing slot id')

    try:
        ts = Timeslot.objects.get(id=int(slot_id), user=request.user)
    except Timeslot.DoesNotExist:
        return HttpResponseBadRequest('Invalid slot')

    ts.available = not ts.available
    ts.save()
    return JsonResponse({'id': ts.id, 'available': ts.available})


def signup(request):
    if request.method == 'POST':
        # Account information
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        # Counselor information
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        middle_initial = request.POST.get('middle_initial', '').strip()
        assigned_college = request.POST.get('assigned_college', '').strip()
        title = request.POST.get('title', '').strip()
        bio = request.POST.get('bio', '').strip()
        profile_picture = request.FILES.get('profile_picture')

        context = { 
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'middle_initial': middle_initial,
            'assigned_college': assigned_college,
            'title': title,
            'bio': bio,
        }

        # Validation
        if not email or not password or not confirm_password:
            context['error'] = 'All account fields are required.'
            return render(request, 'sysadmin/signup.html', context)

        if not first_name or not last_name:
            context['error'] = 'First name and last name are required.'
            return render(request, 'sysadmin/signup.html', context)

        if not assigned_college:
            context['error'] = 'Please select an assigned college.'
            return render(request, 'sysadmin/signup.html', context)

        if password != confirm_password:
            context['error'] = 'Passwords do not match.'
            return render(request, 'sysadmin/signup.html', context)

        # Validate terms acceptance
        terms_accepted = request.POST.get('terms_accepted')
        if not terms_accepted:
            context['error'] = 'You must agree to the Terms of Services and Privacy Policy to continue.'
            return render(request, 'sysadmin/signup.html', context)

        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            context['error'] = 'An account with this email already exists.'
            return render(request, 'sysadmin/signup.html', context)

        # Validate profile picture size (2 MB limit)
        if profile_picture:
            max_size = 2 * 1024 * 1024  # 2 MB in bytes
            if profile_picture.size > max_size:
                size_mb = profile_picture.size / (1024 * 1024)
                context['error'] = f'Profile picture is too large ({size_mb:.2f} MB). Maximum allowed size is 2 MB.'
                return render(request, 'sysadmin/signup.html', context)

        try:
            # Create user with counselor information
            user = User.objects.create_user(username=email, email=email, password=password)
            user.is_staff = True
            user.first_name = first_name
            user.last_name = last_name
            
            # Process profile picture if uploaded
            image_binary = None
            if profile_picture:
                image_binary = profile_picture.read()
            
            # Set the new counselor fields using raw SQL since they're not in the model
            from django.db import connection
            from psycopg2 import Binary
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE auth_user SET middle_initial = %s, assigned_college = %s, title = %s, bio = %s, image_data = %s WHERE id = %s",
                    [middle_initial, assigned_college, title, bio, Binary(image_binary) if image_binary else None, user.id]
                )
            
            user.save()

            authenticated_user = authenticate(request, username=email, password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)
                return redirect('sysadmin:dashboard')

            return redirect('sysadmin:login')
            
        except Exception as e:
            context['error'] = f'Error creating account: {str(e)}'
            return render(request, 'sysadmin/signup.html', context)

    return render(request, 'sysadmin/signup.html')


@login_required
def notifications(request):
    """Display all notifications for the counselor"""
    notifications = Notification.objects.filter(counselor=request.user).order_by('-created_at')
    
    # Mark all notifications as read when viewing the page
    Notification.objects.filter(counselor=request.user, is_read=False).update(is_read=True)
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'sysadmin/notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, counselor=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})


@login_required
@require_POST
def confirm_appointment(request, appointment_id):
    """Confirm a pending appointment"""
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id, counselor=request.user)
        
        if appointment.status == 'pending':
            appointment.status = 'confirmed'
            appointment.save()
            
            # Create notification for student
            from public.utils import create_counselor_notification
            create_counselor_notification(appointment.counselor, appointment, 'appointment_confirmed')
            
            messages.success(request, 'Appointment confirmed successfully!')
        else:
            messages.error(request, 'This appointment cannot be confirmed.')
            
    except Exception as e:
        messages.error(request, f'Error confirming appointment: {str(e)}')
    
    return redirect('sysadmin:dashboard')


@login_required
@require_POST
def cancel_appointment(request, appointment_id):
    """Cancel an appointment"""
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id, counselor=request.user)
        
        if appointment.status in ['pending', 'confirmed']:
            # Mark timeslot as available again
            appointment.timeslot.available = True
            appointment.timeslot.save()
            
            # Cancel appointment
            appointment.status = 'cancelled'
            appointment.save()
            
            # Create notification for student
            from public.utils import create_counselor_notification
            create_counselor_notification(appointment.counselor, appointment, 'appointment_cancelled')
            
            messages.success(request, 'Appointment cancelled successfully!')
        else:
            messages.error(request, 'This appointment cannot be cancelled.')
            
    except Exception as e:
        messages.error(request, f'Error cancelling appointment: {str(e)}')
    
    return redirect('sysadmin:dashboard')


@login_required
@require_POST
def complete_appointment(request, appointment_id):
    """Mark an appointment as completed"""
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id, counselor=request.user)
        
        if appointment.status == 'confirmed':
            appointment.status = 'completed'
            appointment.save()
            
            messages.success(request, 'Appointment marked as completed!')
        else:
            messages.error(request, 'This appointment cannot be marked as completed.')
            
    except Exception as e:
        messages.error(request, f'Error completing appointment: {str(e)}')
    
    return redirect('sysadmin:dashboard')


@login_required
def get_available_slots_for_date(request):
    """Get available timeslots for a specific date (for reschedule modal)"""
    date_str = request.GET.get('date')
    
    if not date_str:
        return JsonResponse({'error': 'Date parameter required'}, status=400)
    
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    # Define time slots
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
    
    available_slots = []
    for hour, label in time_slots:
        slot_time = time(hour=hour, minute=0)
        try:
            ts = Timeslot.objects.get(
                user=request.user,
                date=selected_date,
                start_time=slot_time
            )
            if ts.available:
                available_slots.append({
                    'hour': hour,
                    'label': label
                })
        except Timeslot.DoesNotExist:
            # If slot doesn't exist, it's available
            available_slots.append({
                'hour': hour,
                'label': label
            })
    
    return JsonResponse({'slots': available_slots})


@login_required
def reschedule_appointment(request, appointment_id):
    """Display reschedule form for an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, counselor=request.user)
    
    if request.method == 'POST':
        try:
            # Get new date and time from form
            new_date = request.POST.get('new_date')
            new_time_hour = request.POST.get('new_time')
            
            if not new_date or not new_time_hour:
                return JsonResponse({'success': False, 'error': 'Please select both date and time.'})
            
            # Convert hour to time
            hour = int(new_time_hour)
            new_start_time = time(hour, 0)
            
            # Check if the new timeslot is available
            new_timeslot, created = Timeslot.objects.get_or_create(
                user=request.user,
                date=new_date,
                start_time=new_start_time,
                defaults={'available': True}
            )
            
            if not new_timeslot.available:
                return JsonResponse({'success': False, 'error': 'This time slot is not available.'})
            
            # Free up the old timeslot
            old_timeslot = appointment.timeslot
            old_timeslot.available = True
            old_timeslot.save()
            
            # Update appointment with new timeslot
            appointment.timeslot = new_timeslot
            appointment.status = 'pending'  # Reset to pending for confirmation
            appointment.save()
            
            # Mark new timeslot as unavailable
            new_timeslot.available = False
            new_timeslot.save()
            
            # Create notification for student
            from public.utils import create_counselor_notification
            create_counselor_notification(appointment.counselor, appointment, 'appointment_rescheduled')
            
            return JsonResponse({'success': True, 'message': 'Appointment rescheduled successfully!'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error rescheduling appointment: {str(e)}'})
    
    # Get available dates (next 30 days)
    from datetime import timedelta
    today = timezone.now().date()
    available_dates = []
    for i in range(30):
        date = today + timedelta(days=i)
        available_dates.append(date)
    
    # Define time slots
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
    
    context = {
        'appointment': appointment,
        'available_dates': available_dates,
        'time_slots': time_slots,
    }
    return render(request, 'sysadmin/reschedule_modal.html', context)


@login_required
def analytics(request):
    """Display analytics dashboard with charts and metrics - COUNSELOR SPECIFIC"""
    from django.db.models import Count, Q
    from datetime import timedelta
    import json
    
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Get appointments for THIS COUNSELOR ONLY
    all_appointments = Appointment.objects.filter(counselor=request.user)
    recent_appointments = all_appointments.filter(created_at__gte=thirty_days_ago)
    
    # KPI Metrics
    total_appointments = all_appointments.count()
    pending_count = all_appointments.filter(status='pending').count()
    confirmed_count = all_appointments.filter(status='confirmed').count()
    completed_count = all_appointments.filter(status='completed').count()
    cancelled_count = all_appointments.filter(status='cancelled').count()
    
    # Calculate rates
    completion_rate = (completed_count / total_appointments * 100) if total_appointments > 0 else 0
    cancellation_rate = (cancelled_count / total_appointments * 100) if total_appointments > 0 else 0
    
    # Appointment Status Distribution (for pie chart)
    status_data = all_appointments.values('status').annotate(count=Count('id'))
    status_labels = [item['status'].title() for item in status_data]
    status_counts = [item['count'] for item in status_data]
    
    # Student Activity (replacing counselor comparison - for bar chart)
    # Show top students who have appointments with THIS counselor
    student_data = all_appointments.values(
        'student__first_name', 'student__last_name'
    ).annotate(count=Count('id')).order_by('-count')[:10]
    counselor_labels = [f"{item['student__first_name']} {item['student__last_name']}" for item in student_data]
    counselor_counts = [item['count'] for item in student_data]
    
    # Popular Time Slots (for bar chart)
    timeslot_data = all_appointments.values('timeslot__start_time').annotate(
        count=Count('id')
    ).order_by('-count')[:8]
    timeslot_labels = []
    for item in timeslot_data:
        if item['timeslot__start_time']:
            hour = item['timeslot__start_time'].hour
            if hour < 12:
                time_str = f"{hour}:00 AM"
            elif hour == 12:
                time_str = "12:00 PM"
            else:
                time_str = f"{hour-12}:00 PM"
            timeslot_labels.append(time_str)
        else:
            timeslot_labels.append("N/A")
    timeslot_counts = [item['count'] for item in timeslot_data]
    
    # Appointments by Course/Program (for bar chart)
    program_data = all_appointments.values('program').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    program_labels = [item['program'] if item['program'] else 'Not Specified' for item in program_data]
    program_counts = [item['count'] for item in program_data]
    
    # Monthly trend (last 6 months) for line chart
    monthly_data = []
    monthly_labels = []
    for i in range(5, -1, -1):
        month_start = today.replace(day=1) - timedelta(days=i*30)
        month_end = month_start + timedelta(days=30)
        count = all_appointments.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        monthly_data.append(count)
        monthly_labels.append(month_start.strftime('%b %Y'))
    
    # Capacity Utilization - THIS COUNSELOR ONLY
    total_timeslots = Timeslot.objects.filter(user=request.user, date__gte=today).count()
    available_timeslots = Timeslot.objects.filter(user=request.user, date__gte=today, available=True).count()
    booked_timeslots = all_appointments.filter(
        timeslot__date__gte=today,
        status__in=['pending', 'confirmed']
    ).count()
    utilization_rate = (booked_timeslots / total_timeslots * 100) if total_timeslots > 0 else 0
    
    # Recent activity (last 30 days)
    recent_activity_count = recent_appointments.count()

    # Gender distribution and Age groups for students seen by this counselor
    student_ids = list(all_appointments.values_list('student_id', flat=True).distinct())
    from public.models import UserProfile
    gender_qs = UserProfile.objects.filter(user_id__in=student_ids).values('gender').annotate(count=Count('id'))
    gender_labels = [item['gender'] if item['gender'] else 'Not Specified' for item in gender_qs]
    gender_counts = [item['count'] for item in gender_qs]

    # Age buckets
    def age_bucket(a):
        if a is None:
            return 'Unknown'
        if a < 18:
            return '<18'
        if a <= 24:
            return '18-24'
        if a <= 30:
            return '25-30'
        if a <= 40:
            return '31-40'
        return '41+'

    ages = list(UserProfile.objects.filter(user_id__in=student_ids).values_list('age', flat=True))
    from collections import Counter
    age_counts_map = Counter(age_bucket(a) for a in ages)
    age_labels = list(age_counts_map.keys())
    age_counts = [age_counts_map[label] for label in age_labels]
    
    context = {
        # KPIs
        'total_appointments': total_appointments,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'completion_rate': round(completion_rate, 1),
        'cancellation_rate': round(cancellation_rate, 1),
        'utilization_rate': round(utilization_rate, 1),
        'recent_activity_count': recent_activity_count,
        
        # Chart Data (JSON serialized)
        'status_labels': json.dumps(status_labels),
        'status_counts': json.dumps(status_counts),
        'counselor_labels': json.dumps(counselor_labels),
        'counselor_counts': json.dumps(counselor_counts),
        'timeslot_labels': json.dumps(timeslot_labels),
        'timeslot_counts': json.dumps(timeslot_counts),
        'program_labels': json.dumps(program_labels),
        'program_counts': json.dumps(program_counts),
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data': json.dumps(monthly_data),
        'available_timeslots': available_timeslots,
        'booked_timeslots': booked_timeslots,
        'gender_labels': json.dumps(gender_labels),
        'gender_counts': json.dumps(gender_counts),
        'age_labels': json.dumps(age_labels),
        'age_counts': json.dumps(age_counts),
    }
    
    return render(request, 'sysadmin/analytics.html', context)


@login_required
def reports(request):
    """Generate comprehensive reports for counselors - COUNSELOR SPECIFIC"""
    from django.db.models import Count, Q
    from datetime import timedelta
    
    # Get date range from request or default to last 30 days
    end_date = timezone.now().date()
    start_date_param = request.GET.get('start_date')
    end_date_param = request.GET.get('end_date')
    report_type = request.GET.get('report_type', 'summary')
    
    if start_date_param and end_date_param:
        start_date = datetime.strptime(start_date_param, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
    else:
        start_date = end_date - timedelta(days=30)
    
    # Filter appointments by date range AND THIS COUNSELOR ONLY
    appointments = Appointment.objects.filter(
        counselor=request.user,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).select_related('student', 'counselor', 'timeslot')
    
    # Summary Statistics
    total_appointments = appointments.count()
    pending = appointments.filter(status='pending').count()
    confirmed = appointments.filter(status='confirmed').count()
    completed = appointments.filter(status='completed').count()
    cancelled = appointments.filter(status='cancelled').count()
    
    completion_rate = (completed / total_appointments * 100) if total_appointments > 0 else 0
    cancellation_rate = (cancelled / total_appointments * 100) if total_appointments > 0 else 0
    
    # This counselor's information (for report header)
    counselor_stats = [{
        'counselor__first_name': request.user.first_name,
        'counselor__last_name': request.user.last_name,
        'counselor__email': request.user.email,
        'total': total_appointments,
        'completed': completed,
        'cancelled': cancelled,
        'pending': pending
    }]
    
    # Appointments by Program/Course
    program_stats = appointments.values('program').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Appointments by Time Slot
    timeslot_stats = appointments.values(
        'timeslot__date', 'timeslot__start_time'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:15]
    
    # Daily breakdown for the period
    daily_stats = []
    current_date = start_date
    while current_date <= end_date:
        day_appointments = appointments.filter(created_at__date=current_date)
        daily_stats.append({
            'date': current_date,
            'total': day_appointments.count(),
            'completed': day_appointments.filter(status='completed').count(),
            'cancelled': day_appointments.filter(status='cancelled').count(),
        })
        current_date += timedelta(days=1)
    
    # Student activity (top students by appointment count)
    student_stats = appointments.values(
        'student__first_name', 'student__last_name', 'student__email',
        'student__profile__student_id', 'student__profile__course'
    ).annotate(
        appointment_count=Count('id')
    ).order_by('-appointment_count')[:20]
    
    # Gender and Age summaries for students in this report period
    from public.models import UserProfile
    student_ids = list(appointments.values_list('student_id', flat=True).distinct())
    gender_qs = UserProfile.objects.filter(user_id__in=student_ids).values('gender').annotate(count=Count('id'))
    gender_summary = { (item['gender'] or 'Not Specified'): item['count'] for item in gender_qs }

    def age_bucket(a):
        if a is None:
            return 'Unknown'
        if a < 18:
            return '<18'
        if a <= 24:
            return '18-24'
        if a <= 30:
            return '25-30'
        if a <= 40:
            return '31-40'
        return '41+'

    from collections import Counter
    ages = list(UserProfile.objects.filter(user_id__in=student_ids).values_list('age', flat=True))
    age_summary = Counter(age_bucket(a) for a in ages)
    
    # Detailed appointment list for detailed report
    if report_type == 'detailed':
        appointment_list = appointments.order_by('-created_at')
    else:
        appointment_list = []
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'report_type': report_type,
        'generated_at': timezone.now(),
        
        # Summary stats
        'total_appointments': total_appointments,
        'pending': pending,
        'confirmed': confirmed,
        'completed': completed,
        'cancelled': cancelled,
        'completion_rate': round(completion_rate, 1),
        'cancellation_rate': round(cancellation_rate, 1),
        
        # Detailed stats
        'counselor_stats': counselor_stats,
        'program_stats': program_stats,
        'timeslot_stats': timeslot_stats,
        'daily_stats': daily_stats,
        'student_stats': student_stats,
        'gender_summary': dict(gender_summary),
        'age_summary': dict(age_summary),
        'appointment_list': appointment_list,
    }
    
    return render(request, 'sysadmin/reports.html', context)


@login_required
def export_report_pdf(request):
    """Export report as PDF - COUNSELOR SPECIFIC"""
    from django.http import HttpResponse
    from django.template.loader import render_to_string
    from io import BytesIO
    
    try:
        from xhtml2pdf import pisa
    except ImportError:
        messages.error(request, 'PDF export requires xhtml2pdf. Please install it: pip install xhtml2pdf')
        return redirect('sysadmin:reports')
    
    # Get the same data as reports view
    from django.db.models import Count, Q
    from datetime import timedelta
    
    end_date = timezone.now().date()
    start_date_param = request.GET.get('start_date')
    end_date_param = request.GET.get('end_date')
    report_type = request.GET.get('report_type', 'summary')
    
    if start_date_param and end_date_param:
        start_date = datetime.strptime(start_date_param, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
    else:
        start_date = end_date - timedelta(days=30)
    
    # Filter appointments by THIS COUNSELOR ONLY
    appointments = Appointment.objects.filter(
        counselor=request.user,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).select_related('student', 'counselor', 'timeslot')
    
    total_appointments = appointments.count()
    pending = appointments.filter(status='pending').count()
    confirmed = appointments.filter(status='confirmed').count()
    completed = appointments.filter(status='completed').count()
    cancelled = appointments.filter(status='cancelled').count()
    
    completion_rate = (completed / total_appointments * 100) if total_appointments > 0 else 0
    cancellation_rate = (cancelled / total_appointments * 100) if total_appointments > 0 else 0
    
    # This counselor's information (for PDF header)
    counselor_stats = [{
        'counselor__first_name': request.user.first_name,
        'counselor__last_name': request.user.last_name,
        'counselor__email': request.user.email,
        'total': total_appointments,
        'completed': completed,
        'cancelled': cancelled
    }]
    
    program_stats = appointments.values('program').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'generated_at': timezone.now(),
        'report_type': report_type,
        'total_appointments': total_appointments,
        'pending': pending,
        'confirmed': confirmed,
        'completed': completed,
        'cancelled': cancelled,
        'completion_rate': round(completion_rate, 1),
        'cancellation_rate': round(cancellation_rate, 1),
        'counselor_stats': counselor_stats,
        'program_stats': program_stats,
        'request': request,
    }
    
    # Render HTML template
    html_string = render_to_string('sysadmin/reports_pdf.html', context)
    
    # Create PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
    
    if not pdf.err:
        # Create response
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_{start_date}_to_{end_date}.pdf"'
        return response
    else:
        messages.error(request, 'Error generating PDF. Please try again.')
        return redirect('sysadmin:reports')


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
    """Manage counselor profile"""
    from django.db import connection
    
    # Get current counselor information
    user = request.user
    with connection.cursor() as cursor:
        cursor.execute("SELECT middle_initial, assigned_college, title, bio FROM auth_user WHERE id = %s", [user.id])
        row = cursor.fetchone()
        middle_initial = row[0] if row and row[0] else ''
        assigned_college = row[1] if row and row[1] else ''
        title = row[2] if row and row[2] else ''
        bio = row[3] if row and row[3] else ''
    
    if request.method == 'POST':
        # Get form data
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        middle_initial_new = request.POST.get('middle_initial', '').strip()
        assigned_college_new = request.POST.get('assigned_college', '').strip()
        title_new = request.POST.get('title', '').strip()
        bio_new = request.POST.get('bio', '').strip()
        profile_picture = request.FILES.get('profile_picture')
        current_password = request.POST.get('current_password', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        context = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'middle_initial': middle_initial_new,
            'assigned_college': assigned_college_new,
            'title': title_new,
            'bio': bio_new,
        }
        
        # Validation
        if not email or not first_name or not last_name:
            context['error'] = 'Email, first name, and last name are required.'
            return render(request, 'sysadmin/profile.html', context)
        
        if not assigned_college_new:
            context['error'] = 'Please select an assigned college.'
            return render(request, 'sysadmin/profile.html', context)
        
        # Check if email is taken by another user
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            context['error'] = 'This email is already taken by another user.'
            return render(request, 'sysadmin/profile.html', context)
        
        # Validate profile picture size (2 MB limit)
        if profile_picture:
            max_size = 2 * 1024 * 1024  # 2 MB in bytes
            if profile_picture.size > max_size:
                size_mb = profile_picture.size / (1024 * 1024)
                context['error'] = f'Profile picture is too large ({size_mb:.2f} MB). Maximum allowed size is 2 MB.'
                return render(request, 'sysadmin/profile.html', context)
        
        # Handle password change
        if new_password or confirm_password:
            if not current_password:
                context['error'] = 'Current password is required to change password.'
                return render(request, 'sysadmin/profile.html', context)
            
            if not user.check_password(current_password):
                context['error'] = 'Current password is incorrect.'
                return render(request, 'sysadmin/profile.html', context)
            
            if new_password != confirm_password:
                context['error'] = 'New passwords do not match.'
                return render(request, 'sysadmin/profile.html', context)
            
            if len(new_password) < 6:
                context['error'] = 'New password must be at least 6 characters long.'
                return render(request, 'sysadmin/profile.html', context)
        
        try:
            # Update user information
            user.email = email
            user.username = email
            user.first_name = first_name
            user.last_name = last_name
            
            # Update password if provided
            if new_password:
                user.set_password(new_password)
            
            user.save()
            
            # Process profile picture if uploaded
            image_binary = None
            if profile_picture:
                image_binary = profile_picture.read()
            
            # Update counselor-specific fields using raw SQL
            from psycopg2 import Binary
            with connection.cursor() as cursor:
                if profile_picture:
                    cursor.execute(
                        "UPDATE auth_user SET middle_initial = %s, assigned_college = %s, title = %s, bio = %s, image_data = %s WHERE id = %s",
                        [middle_initial_new, assigned_college_new, title_new, bio_new, Binary(image_binary), user.id]
                    )
                else:
                    cursor.execute(
                        "UPDATE auth_user SET middle_initial = %s, assigned_college = %s, title = %s, bio = %s WHERE id = %s",
                        [middle_initial_new, assigned_college_new, title_new, bio_new, user.id]
                    )
            
            messages.success(request, 'Profile updated successfully!')
            
            # If password was changed, re-authenticate
            if new_password:
                user = authenticate(request, username=email, password=new_password)
                if user:
                    login(request, user)
            
            return redirect('sysadmin:profile')
            
        except Exception as e:
            context['error'] = f'Error updating profile: {str(e)}'
            return render(request, 'sysadmin/profile.html', context)
    
    # GET request - display form with current data
    context = {
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'middle_initial': middle_initial,
        'assigned_college': assigned_college,
        'title': title,
        'bio': bio,
    }
    return render(request, 'sysadmin/profile.html', context)