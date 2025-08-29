from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline para mostrar el perfil en el admin de usuarios"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ('phone', 'organization', 'bio', 'avatar', 'is_verified')


class UserAdmin(BaseUserAdmin):
    """Admin personalizado para usuarios"""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'get_is_verified', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'profile__is_verified', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__organization')
    ordering = ('-date_joined',)
    
    def get_is_verified(self, obj):
        """Mostrar si el usuario está verificado"""
        return obj.profile.is_verified if hasattr(obj, 'profile') else False
    get_is_verified.short_description = 'Verificado'
    get_is_verified.boolean = True


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin para perfiles de usuario"""
    list_display = ('user', 'organization', 'phone', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'organization', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información Personal', {
            'fields': ('phone', 'organization', 'bio', 'avatar')
        }),
        ('Estado', {
            'fields': ('is_verified',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Desregistrar el admin por defecto de User y registrar el personalizado
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
