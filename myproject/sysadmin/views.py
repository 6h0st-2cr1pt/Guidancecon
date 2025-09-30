from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

@login_required
def dashboard(request):
    return render(request, 'sysadmin/dashboard.html')


def index(request):
    return redirect('sysadmin:login')


@login_required
def availability(request):
    return render(request, 'sysadmin/availability.html')


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