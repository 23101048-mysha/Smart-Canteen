from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from datetime import datetime

def home(request):
    return render(request, 'home.html')


def login_page(request):
    login_type = request.GET.get('type')  # URL theke 'student' ba 'staff' dhorbe
    error = None

    if request.method == 'POST':
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')

        user = authenticate(request, username=u_name, password=p_word)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error = "Invalid Username or Password!"

    return render(request, 'login.html', {
        'login_type': login_type,
        'error': error
    })

def signup_page(request):
    if request.method == 'POST':
        fullname = request.POST['fullname']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        # role = request.POST['role'] # Jodi role model-e na thake, eita error dite pare

        if password == confirm_password:
            user = User.objects.create_user(
                first_name=fullname,
                username=username,
                email=email,
                password=password
            )
            user.save()
            login(request, user) # Auto login korbe

            return redirect('dashboard')

    return render(request, 'signup.html')

def dashboard(request):
    today = datetime.now()
    specials = [
        {'name': 'Chicken Biriyani', 'price': 120, 'qty': '1 Plate', 'icon': '🍗', 'available': 25},
        {'name': 'Khichuri & Egg', 'price': 60, 'qty': '1 Bowl', 'icon': '🍳', 'available': 12},
        {'name': 'Milk Tea', 'price': 15, 'qty': '1 Cup', 'icon': '☕', 'available': 50},
        {'name': 'Sandwich', 'price': 45, 'qty': '1 Piece', 'icon': '🥪', 'available': 8},
    ]
    # EKTAI bracket-er moddhe shob context pathate hoy
    return render(request, 'dashboard.html', {
        'specials': specials,
        'current_date': today
    })