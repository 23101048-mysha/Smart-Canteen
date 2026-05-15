from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path('signup/', views.signup_page, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # Student Dashboard & Features
    path('dashboard/', views.dashboard, name='dashboard'),
    path('menu/', views.menu, name='menu'),
    path('profile/', views.profile_view, name='profile'),
    path('notifications/', views.notifications_view, name='notifications'),

    # Orders Section (Student)
    path('orders/', views.orders_view, name='orders_view'),
    path('add-order/', views.add_to_order, name='add_to_order'),
    path('handle-order/', views.handle_order, name='handle_order'),


    path('delete-order/<int:order_id>/', views.delete_order, name='delete_order'),

    # Payment (Online)
    path('payment/online/', views.online_payment_page, name='online_payment_page'),
    path('confirm-online-payment/', views.confirm_online_payment, name='confirm_online_payment'),

    # Feedback System
    path('feedbacks/', views.feedback_list, name='feedback_list'),
    path('feedback/<int:order_id>/', views.feedback_page, name='feedback_page'),
    path('feedback/<int:order_id>/submit/', views.submit_feedback, name='submit_feedback'),
    path('reviews/', views.reviews_list, name='reviews_list'),

    # Staff Dashboard & Operations
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/queue/', views.staff_order_queue, name='order_queue'),
    path('staff/order/process/<int:order_id>/', views.mark_in_process, name='mark_in_process'),
    path('staff/order/ready/<int:order_id>/', views.mark_ready, name='mark_ready'),
    path('staff/order/done/<int:order_id>/', views.mark_done, name='mark_done'),
    path('staff/order/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('staff/payments/', views.staff_payments, name='staff_payments'),

    # Menu Management (Staff)
    path('manage-menu/', views.manage_menu, name='manage_menu'),
    path('delete-food/<int:food_id>/', views.delete_food, name='delete_food'),
    path('add-special/', views.add_special_item, name='add_special_item'),
    path('delete-special/<int:id>/', views.delete_special_item, name='delete_special_item'),
    path('add-special-item/', views.add_special_item, name='add_special_item'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

