from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOfferOwnerOrReadOnly(BasePermission):
    # custom permission to allow read for all authenticated, but write/delete for owner only
    def has_object_permission(self, request, view, obj):
        # for safe methods (GET, HEAD, OPTIONS), allow all authenticated users (matches doc: no 403 for GET, only 401/404)
        if request.method in SAFE_METHODS:
            return True
        # for PATCH/DELETE, check if the request user is the offer owner (returns False for 403 if not)
        return obj.user == request.user