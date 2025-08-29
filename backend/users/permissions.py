from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """
    Permiso personalizado que permite acceso al propietario del objeto o a los administradores.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permisos de lectura para cualquier request,
        # pero solo para el propietario del objeto o administradores
        
        # Si es el mismo usuario o es staff/superuser
        return obj == request.user or request.user.is_staff or request.user.is_superuser


class IsAdminUser(BasePermission):
    """
    Permiso que solo permite acceso a usuarios administradores.
    """
    
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.is_superuser)


class IsOwnerOrReadOnly(BasePermission):
    """
    Permiso personalizado que solo permite al propietario editar el objeto.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permisos de lectura para cualquier request
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Permisos de escritura solo para el propietario del objeto
        return obj == request.user


class IsVerifiedUser(BasePermission):
    """
    Permiso que solo permite acceso a usuarios verificados.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'profile') and 
            request.user.profile.is_verified
        )
