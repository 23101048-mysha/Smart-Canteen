import random
from datetime import datetime, date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Feedback
from django.utils import timezone

from .models import (
    Order, OrderItem, Profile,
    Food, SpecialItem, Notification,Feedback
)

# HOME
def home(request):
    return render(request, 'home.html')


# LOGIN
def login_page(request):
    login_type = request.GET.get('type')
    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            if login_type == "student" and user.is_staff:
                error = "You are not a student!"
            elif login_type == "staff" and not user.is_staff:
                error = "You are not staff!"
            else:
                login(request, user)
                return redirect('staff_dashboard' if user.is_staff else 'dashboard')
        else:
            error = "Invalid username or password!"

    return render(request, 'login.html', {
        'login_type': login_type,
        'error': error
    })


# SIGNUP
def signup_page(request):
    if request.method == 'POST':

        user = User.objects.create_user(
            first_name=request.POST.get('fullname'),
            username=request.POST.get('username'),
            email=request.POST.get('email'),
            password=request.POST.get('password')
        )

        role = request.POST.get('role')
        if role == "staff":
            user.is_staff = True
        user.save()

        Profile.objects.get_or_create(user=user)

        login(request, user)
        return redirect('staff_dashboard' if user.is_staff else 'dashboard')

    return render(request, 'signup.html')


#  STUDENT DASHBOARD
@login_required
def dashboard(request):

    specials = SpecialItem.objects.all().order_by('-id')
    active_orders = Order.objects.filter(
        user=request.user,
        status__in=['Pending', 'In Process', 'Ready']
    ).prefetch_related('items', 'items__food').order_by('-created_at')

    # 3. Notification count
    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    return render(request, 'dashboard.html', {
        'specials': specials,
        'active_orders': active_orders, # Context-e active order pathano holo
        'current_date': datetime.now(),
        'unread_notifications_count': unread_count
    })
@login_required
def menu(request):
    foods = Food.objects.all()
    q = request.GET.get('q')
    if q:
        foods = foods.filter(name__icontains=q)
    return render(request, 'menu.html', {'foods': foods})

@login_required
def online_payment_page(request):
    order_data = request.session.get('pending_order')
    if not order_data:
        return redirect('menu')
    return render(request, 'online_payment.html', {'order': order_data})


@login_required
def handle_order(request):
    if request.method == 'POST':
        food_id = request.POST.get('food_id')
        order_type = request.POST.get('order_type')
        payment_method = request.POST.get('payment_method', '').strip().capitalize()

        food = get_object_or_404(Food, id=food_id)
        if payment_method == 'Online':
            request.session['pending_order'] = {
                'food_id': food.id,
                'order_type': order_type,
                'price': str(food.price),
                'food_name': food.name,
                'payment_method': 'Online'
            }
            return redirect('online_payment_page')
        elif payment_method == 'Cash':
            order = Order.objects.create(
                user=request.user,
                customer_name=request.user.username,
                total_price=food.price,
                order_type=order_type,
                payment_method='Cash',
                payment_status=False,
                status='Pending'
            )


            OrderItem.objects.create(
                order=order,
                food=food,
                quantity=1
            )


            if food.quantity > 0:
                food.quantity -= 1
                if food.quantity == 0:
                    food.available = False
                food.save()

            if 'pending_order' in request.session:
                del request.session['pending_order']

            messages.success(request, f"Cash Order placed for {food.name}! Please pay at counter.")
            return redirect('orders_view')

        else:
            messages.error(request, f"Please select a valid payment method. (Received: {payment_method})")
            return redirect('menu')

    return redirect('menu')

@login_required
def confirm_online_payment(request):
    data = request.session.get('pending_order')
    if not data:
        return redirect('menu')

    food = get_object_or_404(Food, id=data['food_id'])

    order = Order.objects.create(
        user=request.user,
        customer_name=request.user.username,
        total_price=float(data['price']),
        order_type=data['order_type'],
        payment_method='Online',
        payment_status=True,
        status='Pending'
    )

    OrderItem.objects.create(order=order, food=food, quantity=1)

    if food.quantity > 0:
        food.quantity -= 1
        if food.quantity == 0:
            food.available = False
        food.save()

    del request.session['pending_order']
    messages.success(request, "Online Payment Successful! Your order is confirmed.")
    return redirect('orders_view')

@login_required
def mark_ready(request, order_id):

    if not request.user.is_staff:
        return redirect('dashboard')

    order = get_object_or_404(Order, id=order_id)
    order.status = "Ready"
    order.save()

    Notification.objects.create(
        user=order.user,
        message=f"Apnar order #{order.id} ti toiri! Counter theke collect korun."
    )

    messages.success(request, f"Order #{order.id} marked as Ready!")
    return redirect('order_queue')



# ADD ORDER
@login_required
def add_to_order(request):

    if request.method == "POST":

        food = get_object_or_404(Food, id=request.POST.get('food_id'))

        try:
            qty = int(request.POST.get('quantity'))
            if qty < 1:
                qty = 1
        except:
            qty = 1

        if food.quantity < qty:
            messages.error(request, "Not enough stock!")
            return redirect('menu')

        total = float(food.price) * qty

        order = Order.objects.create(
            user=request.user,
            customer_name=request.user.username,
            total_price=total,
            status="Pending",
            order_type=request.POST.get('order_type', 'Takeaway'),
            payment_method=request.POST.get('payment_method', 'Cash')
        )

        OrderItem.objects.create(
            order=order,
            food=food,
            quantity=qty
        )

        food.quantity -= qty
        if food.quantity <= 0:
            food.available = False
        food.save()

        messages.success(request, "Order placed!")
        return redirect('/dashboard/')

    return redirect('menu')


#  ORDERS
@login_required
def orders_view(request):

    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related('items', 'items__food').order_by('-created_at')

    return render(request, 'orders.html', {'orders': orders})

#  DELETE ORDER
@login_required
def delete_order(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    if order.status == "Pending":

        for item in order.items.all():
            item.food.quantity += item.quantity
            item.food.save()

        order.delete()

    return redirect('orders_view')


#  STAFF DASHBOARD
@login_required
def staff_dashboard(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    today = timezone.now().date()

    unread_count = Feedback.objects.filter(is_read=False).count()

    context = {
        'todays_orders': Order.objects.filter(created_at__date=today).count(),
        'pending_orders': Order.objects.filter(status='Pending').count(),
        'pending_list': Order.objects.filter(status='Pending').order_by('-id'),
        'special_items': SpecialItem.objects.all().order_by('-id'),
        'unread_count': unread_count
    }

    return render(request, 'staff_dashboard.html', context)


# MARK READY + NOTIFICATION FIX
@login_required
def mark_ready(request, order_id):

    order = get_object_or_404(Order, id=order_id)
    order.status = "Ready"
    order.save()

    Notification.objects.create(
        user=order.user,
        message=f"Your order #{order.id} is READY!"
    )

    return redirect('staff_dashboard')


#  CANCEL ORDER
@login_required
def cancel_order(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    if order.status != "Cancelled":

        for item in order.items.all():
            item.food.quantity += item.quantity
            item.food.save()

        order.status = "Cancelled"
        order.save()

    return redirect('staff_dashboard')


#SPECIAL ITEM
@login_required
def add_special_item(request):

    if not request.user.is_staff:
        return redirect('staff_dashboard')

    if request.method == "POST":

        SpecialItem.objects.create(
            name=request.POST.get('name'),
            price=request.POST.get('price'),
            image=request.FILES.get('image')
        )

        return redirect('staff_dashboard')

    return render(request, 'add_special_item.html')


@login_required
def delete_special_item(request, id):

    SpecialItem.objects.filter(id=id).delete()
    return redirect('staff_dashboard')


# PROFILE

@login_required
def profile_view(request):

    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        if 'save_profile' in request.POST:
            full_name = request.POST.get('full_name')
            email = request.POST.get('email')

            if not email:
                messages.error(request, "Email field cannot be empty!")
                return redirect('profile')


            request.user.first_name = full_name
            request.user.email = email
            request.user.save()


            profile.phone = request.POST.get('phone')
            profile.department = request.POST.get('department')
            profile.student_id = request.POST.get('student_id')
            profile.save()

            messages.success(request, "Profile updated successfully!")
            return redirect('profile')

        elif 'update_password' in request.POST:
            current_pw = request.POST.get('current_password')
            new_pw = request.POST.get('new_password')
            confirm_pw = request.POST.get('confirm_password')


            if not request.user.check_password(current_pw):
                messages.error(request, "Current password is incorrect!")

            elif new_pw != confirm_pw:
                messages.error(request, "New passwords do not match!")
            else:

                request.user.set_password(new_pw)
                request.user.save()


                update_session_auth_hash(request, request.user)
                messages.success(request, "Password updated successfully!")

            return redirect('profile')


    return render(request, 'profile.html', {
        'user_profile': profile
    })

#  MANAGE MENU
@login_required
def manage_menu(request):

    if not request.user.is_staff:
        return redirect('dashboard')

    if request.method == "POST":

        Food.objects.create(
            name=request.POST.get('name'),
            category=request.POST.get('category'),
            price=request.POST.get('price'),
            quantity=request.POST.get('quantity'),
            photo=request.FILES.get('photo'),
            available=True
        )

        return redirect('manage_menu')

    foods = Food.objects.all().order_by('-id')

    return render(request, 'manage_menu.html', {'foods': foods})


#  DELETE FOOD
@login_required
def delete_food(request, food_id):

    if not request.user.is_staff:
        return redirect('dashboard')

    Food.objects.filter(id=food_id).delete()
    return redirect('manage_menu')


#  NOTIFICATIONS
@login_required
def notifications_view(request):

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    return render(request, 'notification.html', {
        'notifications': notifications,
        'unread_count': 0
    })


#  LOGOUT
def logout_view(request):
    logout(request)
    return redirect('login')


from django.db.models import Sum
from django.utils import timezone

@login_required
def staff_order_queue(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    pending_list = Order.objects.exclude(
        status__in=['Done', 'Cancelled']
    ).prefetch_related('items', 'items__food').order_by('-id')

    today = timezone.now()
    first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0)

    top_selling = OrderItem.objects.filter(
        order__created_at__gte=first_day_of_month,
        order__status='Done' # Keval deliver houa order gulo nibe
    ).values('food__name') \
     .annotate(total_sold=Sum('quantity')) \
     .order_by('-total_sold')[:5] # Shudhu top 5 ti item dekhabe

    context = {
        'pending_list': pending_list,
        'top_selling': top_selling,
        'current_month': today.strftime('%B')
    }

    return render(request, 'order_queue.html', context)


# --- STAFF OPERATIONS

@login_required
def mark_in_process(request, order_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    order = get_object_or_404(Order, id=order_id)
    order.status = "In Process"
    order.save()
    messages.success(request, f"Order #{order.id} is now in process.")
    return redirect('order_queue')


@login_required
def mark_ready(request, order_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    order = get_object_or_404(Order, id=order_id)
    order.status = "Ready"
    order.save()
    Notification.objects.create(
        user=order.user,
        message=f"Your order #{order.id} is READY! Please collect it from counter."
    )
    messages.success(request, f"Order #{order.id} marked as Ready!")
    return redirect('order_queue')


@login_required
def mark_done(request, order_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    order = get_object_or_404(Order, id=order_id)
    order.status = "Done"
    if order.payment_method == "Cash":
        order.payment_status = True

    order.save()
    messages.success(request, f"Order #{order.id} served and payment recorded.")
    return redirect('order_queue')

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status != "Cancelled":

        for item in order.items.all():
            item.food.quantity += item.quantity
            item.food.save()

        order.status = "Cancelled"
        order.save()


        Notification.objects.create(
            user=order.user,
            message=f"Sorry, your order #{order.id} has been cancelled."
        )

    return redirect('order_queue')

@login_required
def feedback_list(request):
    orders = Order.objects.filter(
        user=request.user,
        status="Done"
    ).prefetch_related('items', 'items__food').order_by('-id')

    return render(request, 'feedback_list.html', {
        'orders': orders
    })

@login_required
def feedback_page(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        status="Done"
    )

    return render(request, 'give_feedback.html', {
        'order': order
    })


@login_required
def submit_feedback(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        status="Done"
    )

    if request.method == "POST":
        message = request.POST.get("message")
        rating = request.POST.get("rating")

        if not rating:
            rating = 5

        Feedback.objects.create(
            user=request.user,
            order=order,
            message=message,
            rating=int(rating)
        )

    return redirect('feedback_list')
@login_required
def reviews_list(request):
    reviews = Feedback.objects.all().order_by('-id')

    unread_count = Feedback.objects.filter(is_read=False).count()

    return render(request, 'reviews_list.html', {
        'reviews': reviews,
        'unread_count': unread_count
    })

@login_required
def staff_payments(request):
    if not request.user.is_staff:
        return redirect('dashboard')


    payments = Order.objects.filter(payment_status=True).order_by('-id')

    total_earned = payments.aggregate(
        Sum('total_price')
    )['total_price__sum'] or 0

    return render(request, 'staff_payments.html', {
        'payments': payments,
        'total_earned': total_earned
    })


@login_required
def add_special_item(request):
    if request.method == "POST":
        name = request.POST.get('name')
        price = request.POST.get('price')
        image = request.FILES.get('image')

        SpecialItem.objects.create(
            name=name,
            price=price,
            image=image
        )
        messages.success(request, "Special item added successfully!")
    return redirect('staff_dashboard')

