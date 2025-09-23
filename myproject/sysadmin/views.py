from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def dashboard(request):
    return render(request, 'sysadmin/dashboard.html')


def index(request):
    return redirect('sysadmin:login')
