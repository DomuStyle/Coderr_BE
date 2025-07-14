from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    OFFER_TYPE_CHOICES = (
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    )
    # customer who placed the order
    customer_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_orders')
    # business user who receives the order
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_orders')
    # title of the order
    title = models.CharField(max_length=200)
    # number of revisions
    revisions = models.PositiveIntegerField()
    # delivery time in days
    delivery_time_in_days = models.PositiveIntegerField()
    # price of the order
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # list of features
    features = models.JSONField()
    # offer type
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)
    # status of the order
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    # creation timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    # update timestamp
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # string representation of the order
        return f"Order {self.id} for {self.title} by {self.customer_user.username}"