from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'home.html')


# 🔹 Signup
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})

        user = User.objects.create_user(username=username, email=email, password=password)

        # role save (staff হলে is_staff=True)
        user.is_staff = (role == "staff")
        user.save()

        return redirect('login')

    return render(request, 'signup.html')


# 🔹 Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # role check
            if role == "staff" and user.is_staff:
                login(request, user)
                return redirect('staff_dashboard')

            elif role == "student" and not user.is_staff:
                login(request, user)
                return redirect('student_dashboard')

            else:
                return render(request, 'login.html', {'error': 'Role mismatch ❌'})

        return render(request, 'login.html', {'error': 'Invalid username/password ❌'})

    return render(request, 'login.html')


# 🔹 Dashboards (login required)
@login_required
def student_dashboard(request):
    return render(request, 'student_dashboard.html')


@login_required
def staff_dashboard(request):
    return render(request, 'staff_dashboard.html')


# 🔹 Logout (optional but useful)
def logout_view(request):
    logout(request)
    return redirect('login')