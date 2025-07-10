from django.db import models
from django.contrib.auth.models import User
from profiles_app.models import Profile


class Offer(models.Model):
    # user who created the offer
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    # title of the offer
    title = models.CharField(max_length=200)
    # optional image for the offer
    image = models.ImageField(upload_to='offer_images/', null=True, blank=True)
    # description of the offer
    description = models.TextField()
    # timestamp when offer was created
    created_at = models.DateTimeField(auto_now_add=True)
    # timestamp when offer was last updated
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # string representation of the offer
        return self.title

    @property
    def min_price(self):
        # calculate minimum price from details
        return self.details.aggregate(models.Min('price'))['price__min'] or 0

    @property
    def min_delivery_time(self):
        # calculate minimum delivery time from details
        return self.details.aggregate(models.Min('delivery_time_in_days'))['delivery_time_in_days__min'] or 0

class OfferDetail(models.Model):
    OFFER_TYPE_CHOICES = (
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    )
    # offer this detail belongs to
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='details')
    # title of the detail
    title = models.CharField(max_length=200)
    # number of revisions included
    revisions = models.PositiveIntegerField()
    # delivery time in days
    delivery_time_in_days = models.PositiveIntegerField()
    # price of the detail
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # list of features included
    features = models.JSONField()  # Stores list of strings
    # type of the detail (basic, standard, premium)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)

    def __str__(self):
        # string representation of the detail
        return f"{self.title} ({self.offer_type})"

class Order(models.Model):
    STATUS_CHOICES = (
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    )
    # user who created the offer (business user)
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    # associated offer
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    # order status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    # timestamp when order was created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # string representation of the order
        return f"Order for {self.offer.title} by {self.business_user.username}"
