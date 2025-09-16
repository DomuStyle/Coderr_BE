"""Custom permissions for Django REST Framework to handle ownership-based access control."""

from rest_framework import permissions


class IsOfferOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to allow owners to edit offers while permitting read-only access to others."""

    message = 'Permission denied'

    def has_object_permission(self, request, view, obj):
        # Check if the request method is safe (e.g., GET, HEAD, OPTIONS).
        if request.method in permissions.SAFE_METHODS:
            return True
        # For unsafe methods (e.g., PATCH, DELETE), verify ownership.
        return obj.user == request.user


class IsOfferDetailOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to allow owners to edit offer details while permitting read-only access to others."""

    message = 'Permission denied'

    def has_object_permission(self, request, view, obj):
        # Check if the request method is safe (e.g., GET, HEAD, OPTIONS).
        if request.method in permissions.SAFE_METHODS:
            return True
        # For unsafe methods, verify ownership through the parent offer.
        return obj.offer.user == request.user