from django.db import models
from django.contrib.auth.models import User


class Review(models.Model):
    # business user being reviewed
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    # reviewer (customer)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    # rating (1-5)
    rating = models.PositiveIntegerField()
    # description
    description = models.TextField()
    # creation timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    # update timestamp
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('business_user', 'reviewer')  # One review per business per reviewer

    def __str__(self):
        return f"Review {self.id} for {self.business_user.username} by {self.reviewer.username}"

