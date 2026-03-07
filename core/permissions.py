from rest_framework import permissions

class IsVendorOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow vendors to edit/create.
    """
    def has_permission(self, request, view):
        # Allow anyone to perform GET, HEAD, or OPTIONS requests (Read-Only)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions (POST, PUT, DELETE) are only allowed to authenticated Vendors
        return bool(request.user and request.user.is_authenticated and request.user.is_vendor)