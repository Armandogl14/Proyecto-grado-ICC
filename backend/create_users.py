#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User

# Crear superusuario si no existe
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("✅ Superusuario 'admin' creado exitosamente")
else:
    print("ℹ️  Superusuario 'admin' ya existe")

# Crear algunos usuarios de prueba
test_users = [
    {'username': 'user1', 'email': 'user1@example.com', 'password': 'user123'},
    {'username': 'user2', 'email': 'user2@example.com', 'password': 'user123'},
]

for user_data in test_users:
    if not User.objects.filter(username=user_data['username']).exists():
        User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password']
        )
        print(f"✅ Usuario '{user_data['username']}' creado exitosamente")
    else:
        print(f"ℹ️  Usuario '{user_data['username']}' ya existe")

print("\n🎉 Setup de usuarios completado!")
print("\nUsuarios disponibles:")
for user in User.objects.all():
    print(f"- {user.username} ({'Admin' if user.is_superuser else 'Usuario'}) - {user.email}")
