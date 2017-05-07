from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow write operations to administrators
    """
    def has_permission(self, request, view):
        # Block non-admin users to perform write operations
        if not request.method in permissions.SAFE_METHODS and not request.user.is_staff:
            raise PermissionDenied()

        return True

    def has_object_permission(self, request, view, obj):
        # Block non-admin users to perform write operations
        if not request.method in permissions.SAFE_METHODS and not request.user.is_staff:
            raise PermissionDenied()

        return True