from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


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
