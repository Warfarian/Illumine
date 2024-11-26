from rest_framework.permissions import BasePermission
import logging

logger = logging.getLogger(__name__)

class IsFaculty(BasePermission):
    def has_permission(self, request, view):
        logger.info(f"User: {request.user}")
        logger.info(f"Is authenticated: {request.user.is_authenticated}")
        logger.info(f"Groups: {[g.name for g in request.user.groups.all()]}")
        
        is_faculty = bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.groups.filter(name='faculty').exists()
        )
        logger.info(f"Is faculty: {is_faculty}")
        return is_faculty

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='student').exists()

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.method in ['GET', 'HEAD', 'OPTIONS']
