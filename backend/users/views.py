from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import UserProfile
from .serializers import (
    UserSerializer, UserDetailSerializer, UserRegistrationSerializer,
    UserLoginSerializer, ChangePasswordSerializer, UserAdminSerializer
)
from .permissions import IsOwnerOrAdmin, IsAdminUser


class UserRegistrationView(CreateAPIView):
    """Vista para registro de nuevos usuarios"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Usuario registrado exitosamente',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """Vista para login de usuarios"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login exitoso',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión completa de usuarios"""
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'username', 'email']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        """Usar diferentes serializers según la acción y permisos"""
        if self.action in ['list', 'retrieve'] and self.request.user.is_staff:
            return UserAdminSerializer
        elif self.action in ['update', 'partial_update']:
            return UserDetailSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Permisos según la acción"""
        if self.action == 'create':
            # Solo administradores pueden crear usuarios directamente
            permission_classes = [IsAdminUser]
        elif self.action in ['list']:
            # Solo administradores pueden listar todos los usuarios
            permission_classes = [IsAdminUser]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            # Usuario propietario o administrador
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        elif self.action == 'destroy':
            # Solo administradores pueden eliminar usuarios
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filtrar queryset según el usuario"""
        if self.request.user.is_staff:
            return User.objects.all()
        else:
            # Usuarios normales solo ven su propio perfil
            return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Endpoint para ver y editar el perfil propio"""
        user = request.user
        
        if request.method == 'GET':
            serializer = UserDetailSerializer(user)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = UserDetailSerializer(user, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response({
                'message': 'Perfil actualizado exitosamente',
                'user': serializer.data
            })
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Endpoint para cambiar contraseña"""
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({'message': 'Contraseña cambiada exitosamente'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def toggle_active(self, request, pk=None):
        """Activar/desactivar usuario (solo admin)"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        
        status_text = 'activado' if user.is_active else 'desactivado'
        return Response({
            'message': f'Usuario {status_text} exitosamente',
            'is_active': user.is_active
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def toggle_staff(self, request, pk=None):
        """Convertir usuario en staff o quitar permisos (solo admin)"""
        user = self.get_object()
        user.is_staff = not user.is_staff
        user.save()
        
        status_text = 'promovido a staff' if user.is_staff else 'removido de staff'
        return Response({
            'message': f'Usuario {status_text} exitosamente',
            'is_staff': user.is_staff
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def verify_user(self, request, pk=None):
        """Verificar/desverificar usuario (solo admin)"""
        user = self.get_object()
        user.profile.is_verified = not user.profile.is_verified
        user.profile.save()
        
        status_text = 'verificado' if user.profile.is_verified else 'desverificado'
        return Response({
            'message': f'Usuario {status_text} exitosamente',
            'is_verified': user.profile.is_verified
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):
        """Estadísticas de usuarios (solo admin)"""
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        verified_users = UserProfile.objects.filter(is_verified=True).count()
        
        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'staff_users': staff_users,
            'verified_users': verified_users,
            'unverified_users': total_users - verified_users,
        })


class LogoutView(APIView):
    """Vista para logout (blacklist del refresh token)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({'message': 'Logout exitoso'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)
