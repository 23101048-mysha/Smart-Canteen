from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

# 🔹 Home page
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