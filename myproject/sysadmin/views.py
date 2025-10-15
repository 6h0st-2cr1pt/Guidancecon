from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from datetime import date, time, datetime, timedelta

from .models import Timeslot

@login_required
def dashboard(request):
    return render(request, 'sysadmin/dashboard.html')


def index(request):
    return redirect('sysadmin:login')


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
        title = request.POST.get('title', '').strip()
        bio = request.POST.get('bio', '').strip()
        profile_picture = request.FILES.get('profile_picture')

        context = { 
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'middle_initial': middle_initial,
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

        if password != confirm_password:
            context['error'] = 'Passwords do not match.'
            return render(request, 'sysadmin/signup.html', context)

        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            context['error'] = 'An account with this email already exists.'
            return render(request, 'sysadmin/signup.html', context)

        try:
            # Create user
            user = User.objects.create_user(username=email, email=email, password=password)
            user.is_staff = True
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # Create counselor profile
            from .models import CounselorProfile
            counselor_profile = CounselorProfile.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                middle_initial=middle_initial,
                title=title,
                bio=bio,
                profile_picture=profile_picture
            )

            authenticated_user = authenticate(request, username=email, password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)
                return redirect('sysadmin:dashboard')

            return redirect('sysadmin:login')
            
        except Exception as e:
            context['error'] = f'Error creating account: {str(e)}'
            return render(request, 'sysadmin/signup.html', context)

    return render(request, 'sysadmin/signup.html')