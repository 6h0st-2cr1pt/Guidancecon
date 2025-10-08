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

    # Create or fetch timeslots from 8:00 to 17:00 (5 PM) hourly
    slots = []
    start_hour = 8
    end_hour = 17  # inclusive 5 PM start (so last slot is 17:00-18:00)
    user = request.user

    for h in range(start_hour, end_hour + 1):
        slot_time = time(hour=h, minute=0)
        ts, created = Timeslot.objects.get_or_create(user=user, date=the_date, start_time=slot_time, defaults={'available': False})
        # build a human-friendly label for the slot (e.g. 08:00 AM - 09:00 AM)
        start_dt = datetime.combine(the_date, slot_time)
        end_dt = start_dt + timedelta(hours=1)
        label = f"{start_dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}"
        slots.append({
            'id': ts.id,
            'label': label,
            'available': ts.available,
        })

    context = {
        'slots': slots,
        'date': the_date,
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
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        context = { 'email': email }

        if not email or not password or not confirm_password:
            context['error'] = 'All fields are required.'
            return render(request, 'sysadmin/signup.html', context)

        if password != confirm_password:
            context['error'] = 'Passwords do not match.'
            return render(request, 'sysadmin/signup.html', context)

        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            context['error'] = 'An account with this email already exists.'
            return render(request, 'sysadmin/signup.html', context)

        user = User.objects.create_user(username=email, email=email, password=password)
        user.is_staff = True
        user.save()

        authenticated_user = authenticate(request, username=email, password=password)
        if authenticated_user is not None:
            login(request, authenticated_user)
            return redirect('sysadmin:dashboard')

        return redirect('sysadmin:login')

    return render(request, 'sysadmin/signup.html')