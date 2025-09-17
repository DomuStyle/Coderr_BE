"""Django model for reviews in the reviews_app."""

from django.db import models
from django.contrib.auth.models import User

class Review(models.Model):
    """Represents a review given by a customer to a business user."""
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.PositiveIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensure one review per business user per reviewer.
        unique_together = ('business_user', 'reviewer')

    def __str__(self):
        return f"Review {self.id} for {self.business_user.username} by {self.reviewer.username}"