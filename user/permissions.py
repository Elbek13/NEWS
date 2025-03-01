from rest_framework import permissions
from django.core.exceptions import PermissionDenied

class RoleBasedPermission(permissions.BasePermission):
    """
    Custom permission class to handle role-based access control for the User and BaseModel.
    """

    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False

        # Admin can do everything
        if request.user.role == 'administrator':
            return True

        # Moderator can only view/update data in their own branch
        if request.user.role == 'moderator':
            if request.method in permissions.SAFE_METHODS:  # GET requests
                return True  # Allow viewing, but we'll filter by branch in has_object_permission
            return False  # Moderators can't create/update/delete globally

        # User1 can view all and upload
        if request.user.role == 'user1':
            return True  # Can view and upload (POST)

        # User2 can view everything except Level 1 and upload
        if request.user.role == 'user2':
            return True  # Can view and upload, restricted by object-level checks

        # User3 can only view Level 3
        if request.user.role == 'user3':
            return request.method in permissions.SAFE_METHODS  # Only allow GET

        return False

    def has_object_permission(self, request, view, obj):
        # Admin can do everything
        if request.user.role == 'administrator':
            return True

        # Moderator can only access data in their own branch
        if request.user.role == 'moderator':
            if obj.branch == request.user.branch:
                return request.method in permissions.SAFE_METHODS  # Only GET allowed
            raise PermissionDenied("You can only access data from your branch.")

        # User1 can view all and upload
        if request.user.role == 'user1':
            return True  # Can view all and upload

        # User2 can view everything except Level 1 and upload
        if request.user.role == 'user2':
            if hasattr(obj, 'degree') and obj.degree == 'LEVEL1':
                raise PermissionDenied("User2 cannot access Level 1 data.")
            return True

        # User3 can only view Level 3
        if request.user.role == 'user3':
            if hasattr(obj, 'degree') and obj.degree == 'LEVEL3':
                return request.method in permissions.SAFE_METHODS  # Only GET
            raise PermissionDenied("User3 can only access Level 3 data.")

        return False


class IsActiveUserPermission(permissions.BasePermission):
    """
    Ensures only active users (is_active=True and user_status='active') can perform actions.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_active_user()


# Combine permissions for views
class CustomPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        role_permission = RoleBasedPermission()
        active_permission = IsActiveUserPermission()
        return role_permission.has_permission(request, view) and active_permission.has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        role_permission = RoleBasedPermission()
        return role_permission.has_object_permission(request, view, obj)