from django.db import models
from django.contrib.auth.models import User


# FOOD MODEL

class Food(models.Model):

    CATEGORY_CHOICES = (
        ('Rice', 'Rice'),
        ('Bread', 'Bread'),
        ('Snacks', 'Snacks'),
        ('Drinks', 'Drinks'),
        ('Dessert', 'Dessert'),
    )

    name = models.CharField(max_length=100)

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='Snacks'
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)

    quantity = models.IntegerField(default=0)

    photo = models.ImageField(
        upload_to='food_images/',
        blank=True,
        null=True
    )

    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name



# ORDER MODEL (FIXED)

class Order(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Ready', 'Ready'),
        ('Done', 'Done'),
        ('Cancelled', 'Cancelled'),
    )

    PICKUP_CHOICES = (
        ('Takeaway', 'Takeaway'),
        ('Dine-in', 'Dine-in'),
    )

    PAYMENT_CHOICES = (
        ('Cash', 'Cash'),
        ('Online', 'Online'),
    )

    # user
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        null=True,
        blank=True
    )

    customer_name = models.CharField(max_length=100)

    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # ✅ only ONE status field
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    order_type = models.CharField(
        max_length=20,
        choices=PICKUP_CHOICES,
        default='Takeaway'
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default='Cash'
    )

    payment_status = models.BooleanField(default=False)  # ✅ ADD THIS

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.customer_name}"
# ORDER ITEM MODEL

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    food = models.ForeignKey(
        Food,
        on_delete=models.CASCADE
    )

    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.food.name} x {self.quantity}"



# PROFILE MODEL

class Profile(models.Model):

    ROLE_CHOICES = (
        ('Student', 'Student'),
        ('Staff', 'Staff'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    phone = models.CharField(max_length=15, blank=True, null=True)

    department = models.CharField(max_length=50, blank=True, null=True)

    student_id = models.CharField(max_length=20, blank=True, null=True)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='Student'
    )

    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# SPECIAL ITEM MODEL

class SpecialItem(models.Model):

    name = models.CharField(max_length=100)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    image = models.ImageField(
        upload_to='special_items/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



# NOTIFICATION MODEL

class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    message = models.CharField(max_length=255)

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message


from django.db import models
from django.contrib.auth.models import User
from .models import Order  # যদি Order same app এ থাকে


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    message = models.TextField()
    rating = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.order.id}"