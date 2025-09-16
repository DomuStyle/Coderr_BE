"""Django models for offers, offer details, and orders in the application."""

from django.db import models
from django.contrib.auth.models import User
from profiles_app.models import Profile

class Offer(models.Model):
    """Represents an offer created by a user, including title, description, and related details."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='offer_images/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def min_price(self):
        """Calculate the minimum price from associated details."""
        return self.details.aggregate(models.Min('price'))['price__min'] or 0

    @property
    def min_delivery_time(self):
        """Calculate the minimum delivery time from associated details."""
        return self.details.aggregate(models.Min('delivery_time_in_days'))['delivery_time_in_days__min'] or 0

class OfferDetail(models.Model):
    # Define choices for offer types.
    OFFER_TYPE_CHOICES = (
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    )
    """Represents detailed tiers (basic, standard, premium) for an offer."""
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='details')
    title = models.CharField(max_length=200)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField()
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.title} ({self.offer_type})"

class Order(models.Model):
    # Define choices for order status.
    STATUS_CHOICES = (
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    )
    """Represents an order placed for an offer, tracking status and creation."""
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order for {self.offer.title} by {self.business_user.username}"