from rest_framework import permissions

class SameCompanyPermission(permissions.BasePermission):
    """
    Custom permission to only allow users to access tasks from their own company.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.company

    def has_object_permission(self, request, view, obj):
        return obj.company == request.user.company
