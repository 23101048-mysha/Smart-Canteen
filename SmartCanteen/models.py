from django.db import models
from django.contrib.auth.models import User  # User মডেলটি ইম্পোর্ট করতে হবে


class Order(models.Model):
    # Choice Lists
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Ready', 'Ready'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ]

    PICKUP_CHOICES = [
        ('Dine-in', 'Dine-in'),
        ('Takeaway', 'Takeaway')
    ]

    PAYMENT_CHOICES = [
        ('Cash', 'Cash on Counter'),
        ('Bkash', 'bKash'),
        ('Nagad', 'Nagad'),
        ('Card', 'Card')
    ]

    # Fields
    # User-কে অর্ডারের সাথে লিঙ্ক করা হলো
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    order_id = models.CharField(max_length=20, unique=True)
    items = models.TextField()  # Example: "Burger x2, Pizza x1"

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    pickup_type = models.CharField(max_length=20, choices=PICKUP_CHOICES, default='Takeaway')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='Cash')

    # Payment status track korar jonno naya field
    is_paid = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.order_id} - {self.status}"

    class Meta:
        ordering = ['-created_at']