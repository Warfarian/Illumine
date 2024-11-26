from rest_framework.permissions import BasePermission

class IsFaculty(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'faculty'))

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='student').exists()

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.method in ['GET', 'HEAD', 'OPTIONS']
