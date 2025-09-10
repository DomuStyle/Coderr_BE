# from rest_framework.permissions import BasePermission, SAFE_METHODS

# class IsOfferOwnerOrReadOnly(BasePermission):
#     # custom permission to allow read for all authenticated, but write/delete for owner only
#     def has_object_permission(self, request, view, obj):
#         # for safe methods (GET, HEAD, OPTIONS), allow all authenticated users (matches doc: no 403 for GET, only 401/404)
#         if request.method in SAFE_METHODS:
#             return True
#         # for PATCH/DELETE, check if the request user is the offer owner (returns False for 403 if not)
#         return obj.user == request.user

from rest_framework import permissions  # import the base permissions module from drf

class IsOfferOwnerOrReadOnly(permissions.BasePermission):  # lower case letters: define the custom permission class with the original name to match imports
    message = 'Permission denied'  # lower case letters: set the custom message to 'permission denied' for the response detail when permission is denied

    def has_object_permission(self, request, view, obj):  # lower case letters: override the has_object_permission method to check permissions
        if request.method in permissions.SAFE_METHODS:  # lower case letters: allow read-only access (get, head, options) for all users
            return True  # lower case letters: return true for safe methods
        return obj.user == request.user  # lower case letters: for unsafe methods (patch, delete), check if the object's user matches the request user