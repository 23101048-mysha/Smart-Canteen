import random

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from datetime import datetime
from django.shortcuts import render
from .models import Order

# 🔹 Home page
def home(request):
    return render(request, 'home.html')


def login_page(request):
    login_type = request.GET.get('type')
    error = None

    if request.method == 'POST':
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')

        user = authenticate(request, username=u_name, password=p_word)

        if user is not None:
            if login_type == "student" and user.is_staff:
                error = "You are not a student!"
                return render(request, 'login.html', {'error': error})

            if login_type == "staff" and not user.is_staff:
                error = "You are not staff!"
                return render(request, 'login.html', {'error': error})
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

    return render(request, 'dashboard.html', {
        'specials': specials,
        'current_date': today
    })

    return render(request, 'signup.html')
def menu(request):
    query = request.GET.get('q')

    foods = [
        {
            "name": "Chicken Biriyani",
            "emoji": "🍗",
            "category": "Rice",
            "price": "120",
            "stock": "25 items left"
        },
        {
            "name": "Khichuri & Egg",
            "emoji": "🍳",
            "category": "Rice",
            "price": "60",
            "stock": "12 items left"
        },
        {
            "name": "Milk Tea",
            "emoji": "☕",
            "category": "Drinks",
            "price": "15",
            "stock": "50 items left"
        },
        {
            "name": "Cold Coffee",
            "emoji": "🥤",
            "category": "Drinks",
            "price": "40",
            "stock": "Out of Stock"
        },
        {
            "name": "Sandwich",
            "emoji": "🥪",
            "category": "Snacks",
            "price": "45",
            "stock": "8 items left"
        },
    ]

    if query:
        foods = [
            food for food in foods
            if query.lower() in food["name"].lower()
            or query.lower() in food["category"].lower()
        ]

    return render(request, 'menu.html', {'foods': foods})


import random
from django.shortcuts import render, redirect
from .models import Order

def add_to_order(request):
    if request.method == "POST":
        item_name = request.POST.get('item_name')
        price = request.POST.get('price')
        pickup = request.POST.get('pickup_type', 'Takeaway')
        payment = request.POST.get('payment_method', 'Cash')

        new_id = f"SB-{random.randint(1000, 9999)}"

        Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            order_id=new_id,
            items=item_name,
            amount=int(float(price)),
            pickup_type=pickup,
            payment_method=payment,
            status="Pending"
        )
        return redirect('orders_view')
    return redirect('menu')

def orders_view(request):
    all_orders = Order.objects.all().order_by('-created_at')
    return render(request, 'orders.html', {'orders': all_orders})


def cancel_order(request, order_id):

    order = get_object_or_404(Order, order_id=order_id)

    if order.status == 'Pending':
        order.status = 'Cancelled'
        order.save()

    return redirect('orders_view')