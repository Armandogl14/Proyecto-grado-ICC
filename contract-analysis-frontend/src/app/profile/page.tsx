'use client';

import { useAuth } from '@/contexts/AuthContext';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

export default function ProfilePage() {
  const { user } = useAuth();

  return (
    <ProtectedRoute>
      <div className="container mx-auto p-6">
        <h1 className="text-2xl font-bold mb-6">Perfil de Usuario</h1>
        
        {user && (
          <div className="bg-slate-800 p-6 rounded-lg">
            <h2 className="text-xl mb-4">Información del Usuario</h2>
            <div className="space-y-2">
              <p><strong>ID:</strong> {user.id}</p>
              <p><strong>Username:</strong> {user.username}</p>
              <p><strong>Email:</strong> {user.email}</p>
              <p><strong>Nombre:</strong> {user.first_name} {user.last_name}</p>
              <p><strong>Es admin:</strong> {user.is_staff ? 'Sí' : 'No'}</p>
              <p><strong>Activo:</strong> {user.is_active ? 'Sí' : 'No'}</p>
            </div>
          </div>
        )}
      </div>
    </ProtectedRoute>
  );
}