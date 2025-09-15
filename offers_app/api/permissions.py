# from rest_framework import permissions

# class IsOfferOwnerOrReadOnly(permissions.BasePermission):  # define the custom permission class with the original name to match imports
#     message = 'Permission denied'  
#     def has_object_permission(self, request, view, obj):  # override the has_object_permission method to check permissions
#         if request.method in permissions.SAFE_METHODS:  #  allow read-only access (get, head, options) for all users
#             return True  
#         return obj.user == request.user  # for unsafe methods (patch, delete), check if the object's user matches the request user

from rest_framework import permissions 

class IsOfferOwnerOrReadOnly(permissions.BasePermission):  #define the custom permission class with the original name to match imports
    message = 'Permission denied' 

    def has_object_permission(self, request, view, obj):  # override the has_object_permission method to check permissions
        if request.method in permissions.SAFE_METHODS:  # allow read-only access (get, head, options) for all users
            return True  # return true for safe methods
        return obj.user == request.user  # for unsafe methods (patch, delete), check if the object's user matches the request user

class IsOfferDetailOwnerOrReadOnly(permissions.BasePermission):
    message = 'Permission denied'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.offer.user == request.user  # check the parent offer's user for ownership