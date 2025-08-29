# 🎯 Plan de Implementación: CRUD de Usuarios - Frontend

## 📋 **Resumen Ejecutivo**

**Objetivo**: Implementar el sistema completo de gestión de usuarios en el frontend para el sistema de análisis de contratos, integrando con las APIs REST ya desarrolladas en el backend.

**Tecnología Backend**: Django REST Framework con JWT Authentication
**Frontend Recomendado**: React.js con TypeScript
**Autenticación**: JWT Tokens (Access + Refresh)

---

## 🏗️ **Arquitectura Frontend Propuesta**

### **Stack Tecnológico**
- **Framework**: React 18+ con TypeScript
- **State Management**: Context API + useReducer (o Redux Toolkit)
- **HTTP Client**: Axios
- **Routing**: React Router v6
- **UI Framework**: Material-UI, Ant Design, o Tailwind CSS
- **Formularios**: React Hook Form + Zod validation
- **Auth Management**: Custom hooks + Local Storage/SessionStorage

---

## 🎯 **Fase 1: Configuración Base y Autenticación** 
*Tiempo estimado: 3-4 días*

### **1.1 Setup del Proyecto**
```bash
# Crear proyecto React con TypeScript
npx create-react-app contract-frontend --template typescript
cd contract-frontend

# Instalar dependencias principales
npm install axios react-router-dom @types/react-router-dom
npm install react-hook-form @hookform/resolvers zod
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material @mui/lab
```

### **1.2 Estructura de Carpetas**
```
src/
├── components/
│   ├── common/
│   │   ├── Layout.tsx
│   │   ├── ProtectedRoute.tsx
│   │   └── LoadingSpinner.tsx
│   └── users/
│       ├── LoginForm.tsx
│       ├── RegisterForm.tsx
│       ├── UserProfile.tsx
│       └── UserList.tsx
├── pages/
│   ├── auth/
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   └── ForgotPasswordPage.tsx
│   ├── users/
│   │   ├── ProfilePage.tsx
│   │   ├── UsersManagementPage.tsx
│   │   └── EditUserPage.tsx
│   └── Dashboard.tsx
├── services/
│   ├── api.ts
│   ├── authService.ts
│   └── userService.ts
├── context/
│   ├── AuthContext.tsx
│   └── UserContext.tsx
├── hooks/
│   ├── useAuth.ts
│   ├── useUsers.ts
│   └── useLocalStorage.ts
├── types/
│   ├── auth.types.ts
│   ├── user.types.ts
│   └── api.types.ts
└── utils/
    ├── constants.ts
    ├── helpers.ts
    └── validators.ts
```

### **1.3 Configuración de Tipos TypeScript**
```typescript
// types/user.types.ts
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  date_joined: string;
  last_login?: string;
  profile: UserProfile;
}

export interface UserProfile {
  phone: string;
  organization: string;
  bio: string;
  avatar?: string;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

// types/auth.types.ts
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name?: string;
  last_name?: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse {
  message: string;
  user: User;
  tokens: AuthTokens;
}
```

### **1.4 API Service Base**
```typescript
// services/api.ts
import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { AuthTokens } from '../types/auth.types';

class ApiService {
  private api: AxiosInstance;
  private baseURL = process.env.REACT_APP_API_URL || 'http://172.245.214.69/api';

  constructor() {
    this.api = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor - agregar token
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor - manejar token refresh
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await this.refreshToken(refreshToken);
              localStorage.setItem('access_token', response.access);
              return this.api(originalRequest);
            }
          } catch (refreshError) {
            // Limpiar tokens y notificar al sistema de auth
            this.handleAuthFailure();
          }
        }
        
        return Promise.reject(error);
      }
    );
  }

  private handleAuthFailure() {
    localStorage.clear();
    // Disparar evento personalizado para que AuthContext maneje el logout
    window.dispatchEvent(new CustomEvent('auth:logout'));
    // Solo usar window.location como fallback si no hay React Router
    if (!window.location.pathname.includes('/login')) {
      window.location.href = '/login';
    }
  }

  private async refreshToken(refresh: string) {
    const response = await axios.post(`${this.baseURL}/auth/token/refresh/`, {
      refresh,
    });
    return response.data;
  }

  get<T = any>(url: string): Promise<AxiosResponse<T>> {
    return this.api.get(url);
  }

  post<T = any>(url: string, data?: any): Promise<AxiosResponse<T>> {
    return this.api.post(url, data);
  }

  put<T = any>(url: string, data?: any): Promise<AxiosResponse<T>> {
    return this.api.put(url, data);
  }

  patch<T = any>(url: string, data?: any): Promise<AxiosResponse<T>> {
    return this.api.patch(url, data);
  }

  delete<T = any>(url: string): Promise<AxiosResponse<T>> {
    return this.api.delete(url);
  }
}

export const apiService = new ApiService();
```

---

## 🔐 **Fase 2: Sistema de Autenticación**
*Tiempo estimado: 2-3 días*

### **2.1 Auth Context**
```typescript
// context/AuthContext.tsx
import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { User, AuthTokens } from '../types/auth.types';
import { authService } from '../services/authService';

interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  loading: boolean;
  isAuthenticated: boolean;
}

interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  updateUser: (user: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Auth reducer para manejar estados
function authReducer(state: AuthState, action: any): AuthState {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, loading: true };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        tokens: action.payload.tokens,
        loading: false,
        isAuthenticated: true,
      };
    case 'LOGIN_ERROR':
      return {
        ...state,
        loading: false,
        isAuthenticated: false,
        user: null,
        tokens: null,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        tokens: null,
        isAuthenticated: false,
      };
    case 'UPDATE_USER':
      return {
        ...state,
        user: action.payload,
      };
    default:
      return state;
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, {
    user: null,
    tokens: null,
    loading: true,
    isAuthenticated: false,
  });

  useEffect(() => {
    // Verificar si hay token al cargar la app
    const token = localStorage.getItem('access_token');
    if (token) {
      authService.getCurrentUser()
        .then(user => {
          dispatch({ type: 'LOGIN_SUCCESS', payload: { user, tokens: null } });
        })
        .catch(() => {
          localStorage.clear();
          dispatch({ type: 'LOGIN_ERROR' });
        });
    } else {
      dispatch({ type: 'LOGIN_ERROR' });
    }

    // Escuchar eventos de logout desde API interceptors
    const handleAuthLogout = () => {
      dispatch({ type: 'LOGOUT' });
    };

    window.addEventListener('auth:logout', handleAuthLogout);
    
    return () => {
      window.removeEventListener('auth:logout', handleAuthLogout);
    };
  }, []);

  const login = async (username: string, password: string) => {
    dispatch({ type: 'LOGIN_START' });
    try {
      const response = await authService.login(username, password);
      localStorage.setItem('access_token', response.tokens.access);
      localStorage.setItem('refresh_token', response.tokens.refresh);
      dispatch({ type: 'LOGIN_SUCCESS', payload: response });
    } catch (error) {
      dispatch({ type: 'LOGIN_ERROR' });
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.clear();
      dispatch({ type: 'LOGOUT' });
    }
  };

  const updateUser = (user: User) => {
    dispatch({ type: 'UPDATE_USER', payload: user });
  };

  return (
    <AuthContext.Provider value={{
      ...state,
      login,
      logout,
      updateUser,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

### **2.2 Auth Service**
```typescript
// services/authService.ts
import { apiService } from './api';
import { LoginCredentials, RegisterData, AuthResponse, User } from '../types/auth.types';

class AuthService {
  async login(username: string, password: string): Promise<AuthResponse> {
    const response = await apiService.post<AuthResponse>('/auth/login/', {
      username,
      password,
    });
    return response.data;
  }

  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await apiService.post<AuthResponse>('/auth/register/', data);
    return response.data;
  }

  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token');
    const accessToken = localStorage.getItem('access_token');
    
    if (refreshToken && accessToken) {
      await apiService.post('/auth/logout/', {
        refresh_token: refreshToken,
      });
    }
  }

  async getCurrentUser(): Promise<User> {
    const response = await apiService.get<User>('/users/me/');
    return response.data;
  }

  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    await apiService.post('/users/change_password/', {
      old_password: oldPassword,
      new_password: newPassword,
    });
  }

  async refreshToken(refresh: string): Promise<{ access: string }> {
    const response = await apiService.post('/auth/token/refresh/', {
      refresh,
    });
    return response.data;
  }
}

export const authService = new AuthService();
```

---

## 👥 **Fase 3: CRUD de Usuarios**
*Tiempo estimado: 4-5 días*

### **3.1 User Service**
```typescript
// services/userService.ts
import { apiService } from './api';
import { User, UserProfile } from '../types/user.types';

interface UpdateProfileData {
  first_name?: string;
  last_name?: string;
  email?: string;
  profile?: {
    phone?: string;
    organization?: string;
    bio?: string;
  };
}

interface UsersListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: User[];
}

class UserService {
  // Obtener lista de usuarios (solo admin)
  async getUsers(page = 1, search = ''): Promise<UsersListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      ...(search && { search }),
    });
    
    const response = await apiService.get<UsersListResponse>(`/users/?${params}`);
    return response.data;
  }

  // Obtener usuario específico
  async getUser(id: number): Promise<User> {
    const response = await apiService.get<User>(`/users/${id}/`);
    return response.data;
  }

  // Obtener perfil propio
  async getMyProfile(): Promise<User> {
    const response = await apiService.get<User>('/users/me/');
    return response.data;
  }

  // Actualizar perfil propio
  async updateProfile(data: UpdateProfileData): Promise<User> {
    const response = await apiService.put<{ user: User }>('/users/update_profile/', data);
    return response.data.user;
  }

  // Actualizar usuario (admin)
  async updateUser(id: number, data: UpdateProfileData): Promise<User> {
    const response = await apiService.put<User>(`/users/${id}/`, data);
    return response.data;
  }

  // Eliminar usuario (admin)
  async deleteUser(id: number): Promise<void> {
    await apiService.delete(`/users/${id}/`);
  }

  // Cambiar estado activo/inactivo (admin)
  async toggleUserStatus(id: number, isActive: boolean): Promise<User> {
    const response = await apiService.patch<User>(`/users/${id}/`, {
      is_active: isActive,
    });
    return response.data;
  }

  // Subir avatar
  async uploadAvatar(file: File): Promise<User> {
    const formData = new FormData();
    formData.append('avatar', file);
    
    const response = await apiService.post<{ user: User }>('/users/upload_avatar/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.user;
  }
}

export const userService = new UserService();
```

### **3.2 Hooks Personalizados**
```typescript
// hooks/useUsers.ts
import { useState, useEffect } from 'react';
import { User } from '../types/user.types';
import { userService } from '../services/userService';

export function useUsers() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
    currentPage: 1,
  });

  const fetchUsers = async (page = 1, search = '') => {
    setLoading(true);
    try {
      const response = await userService.getUsers(page, search);
      setUsers(response.results);
      setPagination({
        count: response.count,
        next: response.next,
        previous: response.previous,
        currentPage: page,
      });
      setError(null);
    } catch (err) {
      setError('Error al cargar usuarios');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateUser = async (id: number, data: any) => {
    try {
      const updatedUser = await userService.updateUser(id, data);
      setUsers(users.map(user => user.id === id ? updatedUser : user));
      return updatedUser;
    } catch (err) {
      setError('Error al actualizar usuario');
      throw err;
    }
  };

  const deleteUser = async (id: number) => {
    try {
      await userService.deleteUser(id);
      setUsers(users.filter(user => user.id !== id));
    } catch (err) {
      setError('Error al eliminar usuario');
      throw err;
    }
  };

  const toggleUserStatus = async (id: number, isActive: boolean) => {
    try {
      const updatedUser = await userService.toggleUserStatus(id, isActive);
      setUsers(users.map(user => user.id === id ? updatedUser : user));
      return updatedUser;
    } catch (err) {
      setError('Error al cambiar estado del usuario');
      throw err;
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  return {
    users,
    loading,
    error,
    pagination,
    fetchUsers,
    updateUser,
    deleteUser,
    toggleUserStatus,
    refetch: () => fetchUsers(pagination.currentPage),
  };
}

// hooks/useProfile.ts
export function useProfile() {
  const [profile, setProfile] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = async () => {
    setLoading(true);
    try {
      const userData = await userService.getMyProfile();
      setProfile(userData);
      setError(null);
    } catch (err) {
      setError('Error al cargar perfil');
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async (data: any) => {
    try {
      const updatedUser = await userService.updateProfile(data);
      setProfile(updatedUser);
      return updatedUser;
    } catch (err) {
      setError('Error al actualizar perfil');
      throw err;
    }
  };

  const uploadAvatar = async (file: File) => {
    try {
      const updatedUser = await userService.uploadAvatar(file);
      setProfile(updatedUser);
      return updatedUser;
    } catch (err) {
      setError('Error al subir avatar');
      throw err;
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  return {
    profile,
    loading,
    error,
    updateProfile,
    uploadAvatar,
    refetch: fetchProfile,
  };
}
```

---

## 🎨 **Fase 4: Componentes de UI**
*Tiempo estimado: 5-6 días*

### **4.1 Formulario de Login**
```tsx
// components/users/LoginForm.tsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
  Box,
  Button,
  TextField,
  Typography,
  Alert,
  Paper,
  CircularProgress,
} from '@mui/material';
import { useAuth } from '../../context/AuthContext';

const loginSchema = z.object({
  username: z.string().min(1, 'El usuario es requerido'),
  password: z.string().min(1, 'La contraseña es requerida'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export function LoginForm() {
  const { login } = useAuth();
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setLoading(true);
    setError(null);
    
    try {
      await login(data.username, data.password);
      // La navegación se maneja en el AuthContext/App level
    } catch (err: any) {
      setError(err.response?.data?.message || 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 400, mx: 'auto', mt: 8 }}>
      <Typography variant="h4" component="h1" gutterBottom align="center">
        Iniciar Sesión
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ mt: 1 }}>
        <TextField
          {...register('username')}
          margin="normal"
          required
          fullWidth
          label="Usuario"
          autoComplete="username"
          autoFocus
          error={!!errors.username}
          helperText={errors.username?.message}
        />
        
        <TextField
          {...register('password')}
          margin="normal"
          required
          fullWidth
          label="Contraseña"
          type="password"
          autoComplete="current-password"
          error={!!errors.password}
          helperText={errors.password?.message}
        />
        
        <Button
          type="submit"
          fullWidth
          variant="contained"
          sx={{ mt: 3, mb: 2 }}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Iniciar Sesión'}
        </Button>
      </Box>
    </Paper>
  );
}
```

### **4.2 Lista de Usuarios (Admin)**
```tsx
// components/users/UserList.tsx
import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Avatar,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  Typography,
  Box,
  Switch,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { User } from '../../types/user.types';
import { useUsers } from '../../hooks/useUsers';
import { formatDate } from '../../utils/helpers';

interface UserListProps {
  onEditUser: (user: User) => void;
}

export function UserList({ onEditUser }: UserListProps) {
  const { users, loading, toggleUserStatus, deleteUser } = useUsers();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, user: User) => {
    setAnchorEl(event.currentTarget);
    setSelectedUser(user);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedUser(null);
  };

  const handleStatusToggle = async (user: User) => {
    try {
      await toggleUserStatus(user.id, !user.is_active);
    } catch (error) {
      console.error('Error toggling user status:', error);
    }
  };

  const handleDeleteConfirm = async () => {
    if (selectedUser) {
      try {
        await deleteUser(selectedUser.id);
        setDeleteDialogOpen(false);
        handleMenuClose();
      } catch (error) {
        console.error('Error deleting user:', error);
      }
    }
  };

  const getRoleChip = (user: User) => {
    if (user.is_superuser) {
      return <Chip label="Super Admin" color="error" size="small" />;
    }
    if (user.is_staff) {
      return <Chip label="Admin" color="warning" size="small" />;
    }
    return <Chip label="Usuario" color="primary" size="small" />;
  };

  if (loading) {
    return <Typography>Cargando usuarios...</Typography>;
  }

  return (
    <Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Usuario</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Rol</TableCell>
              <TableCell>Estado</TableCell>
              <TableCell>Registro</TableCell>
              <TableCell>Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Avatar src={user.profile?.avatar}>
                      <PersonIcon />
                    </Avatar>
                    <Box>
                      <Typography variant="body2" fontWeight="medium">
                        {user.first_name} {user.last_name} ({user.username})
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {user.profile?.organization}
                      </Typography>
                    </Box>
                  </Box>
                </TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>{getRoleChip(user)}</TableCell>
                <TableCell>
                  <Switch
                    checked={user.is_active}
                    onChange={() => handleStatusToggle(user)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {formatDate(user.date_joined)}
                  </Typography>
                </TableCell>
                <TableCell>
                  <IconButton
                    onClick={(e) => handleMenuOpen(e, user)}
                    size="small"
                  >
                    <MoreVertIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Menu de acciones */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem
          onClick={() => {
            if (selectedUser) onEditUser(selectedUser);
            handleMenuClose();
          }}
        >
          <EditIcon sx={{ mr: 1 }} />
          Editar
        </MenuItem>
        <MenuItem
          onClick={() => {
            setDeleteDialogOpen(true);
            handleMenuClose();
          }}
          sx={{ color: 'error.main' }}
        >
          <DeleteIcon sx={{ mr: 1 }} />
          Eliminar
        </MenuItem>
      </Menu>

      {/* Dialog de confirmación de eliminación */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirmar Eliminación</DialogTitle>
        <DialogContent>
          <Typography>
            ¿Estás seguro de que quieres eliminar al usuario{' '}
            <strong>{selectedUser?.username}</strong>?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancelar</Button>
          <Button onClick={handleDeleteConfirm} color="error">
            Eliminar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
```

### **4.3 Perfil de Usuario**
```tsx
// components/users/UserProfile.tsx
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
  Box,
  Card,
  CardContent,
  Avatar,
  Typography,
  TextField,
  Button,
  Grid,
  Alert,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Edit as EditIcon,
  PhotoCamera as PhotoCameraIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { useProfile } from '../../hooks/useProfile';
import { useAuth } from '../../context/AuthContext';

const profileSchema = z.object({
  first_name: z.string().max(30, 'Máximo 30 caracteres'),
  last_name: z.string().max(30, 'Máximo 30 caracteres'),
  email: z.string().email('Email inválido'),
  phone: z.string().max(20, 'Máximo 20 caracteres'),
  organization: z.string().max(100, 'Máximo 100 caracteres'),
  bio: z.string().max(500, 'Máximo 500 caracteres'),
});

type ProfileFormData = z.infer<typeof profileSchema>;

export function UserProfile() {
  const { user, updateUser } = useAuth();
  const { updateProfile, uploadAvatar } = useProfile();
  const [isEditing, setIsEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [avatarDialogOpen, setAvatarDialogOpen] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      email: user?.email || '',
      phone: user?.profile?.phone || '',
      organization: user?.profile?.organization || '',
      bio: user?.profile?.bio || '',
    },
  });

  const onSubmit = async (data: ProfileFormData) => {
    setError(null);
    setSuccess(null);
    
    try {
      const updatedUser = await updateProfile({
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email,
        profile: {
          phone: data.phone,
          organization: data.organization,
          bio: data.bio,
        },
      });
      
      updateUser(updatedUser);
      setIsEditing(false);
      setSuccess('Perfil actualizado exitosamente');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Error al actualizar perfil');
    }
  };

  const handleAvatarUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      try {
        const updatedUser = await uploadAvatar(file);
        updateUser(updatedUser);
        setAvatarDialogOpen(false);
        setSuccess('Avatar actualizado exitosamente');
      } catch (err: any) {
        setError('Error al subir avatar');
      }
    }
  };

  const handleCancel = () => {
    reset();
    setIsEditing(false);
    setError(null);
  };

  if (!user) {
    return <Typography>Cargando perfil...</Typography>;
  }

  return (
    <Card sx={{ maxWidth: 800, mx: 'auto', mt: 2 }}>
      <CardContent>
        {/* Header with Avatar */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 2 }}>
          <Box sx={{ position: 'relative' }}>
            <Avatar
              src={user.profile?.avatar}
              sx={{ width: 100, height: 100 }}
            >
              {user.first_name?.[0]}{user.last_name?.[0]}
            </Avatar>
            <IconButton
              sx={{
                position: 'absolute',
                bottom: 0,
                right: 0,
                bgcolor: 'primary.main',
                color: 'white',
                '&:hover': { bgcolor: 'primary.dark' },
              }}
              size="small"
              onClick={() => setAvatarDialogOpen(true)}
            >
              <PhotoCameraIcon fontSize="small" />
            </IconButton>
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h4">
              {user.first_name} {user.last_name}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              @{user.username}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {user.profile?.organization}
            </Typography>
          </Box>
          <Button
            startIcon={isEditing ? <CancelIcon /> : <EditIcon />}
            onClick={isEditing ? handleCancel : () => setIsEditing(true)}
            variant={isEditing ? "outlined" : "contained"}
          >
            {isEditing ? 'Cancelar' : 'Editar'}
          </Button>
        </Box>

        {/* Alerts */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        {/* Form */}
        <Box component="form" onSubmit={handleSubmit(onSubmit)}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                {...register('first_name')}
                fullWidth
                label="Nombre"
                disabled={!isEditing}
                error={!!errors.first_name}
                helperText={errors.first_name?.message}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                {...register('last_name')}
                fullWidth
                label="Apellido"
                disabled={!isEditing}
                error={!!errors.last_name}
                helperText={errors.last_name?.message}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                {...register('email')}
                fullWidth
                label="Email"
                type="email"
                disabled={!isEditing}
                error={!!errors.email}
                helperText={errors.email?.message}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                {...register('phone')}
                fullWidth
                label="Teléfono"
                disabled={!isEditing}
                error={!!errors.phone}
                helperText={errors.phone?.message}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                {...register('organization')}
                fullWidth
                label="Organización"
                disabled={!isEditing}
                error={!!errors.organization}
                helperText={errors.organization?.message}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                {...register('bio')}
                fullWidth
                label="Biografía"
                multiline
                rows={3}
                disabled={!isEditing}
                error={!!errors.bio}
                helperText={errors.bio?.message}
              />
            </Grid>
          </Grid>

          {isEditing && (
            <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button
                type="submit"
                variant="contained"
                startIcon={<SaveIcon />}
              >
                Guardar Cambios
              </Button>
            </Box>
          )}
        </Box>

        {/* Avatar Upload Dialog */}
        <Dialog open={avatarDialogOpen} onClose={() => setAvatarDialogOpen(false)}>
          <DialogTitle>Cambiar Avatar</DialogTitle>
          <DialogContent>
            <input
              accept="image/*"
              type="file"
              onChange={handleAvatarUpload}
              style={{ width: '100%', padding: '10px' }}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setAvatarDialogOpen(false)}>
              Cancelar
            </Button>
          </DialogActions>
        </Dialog>
      </CardContent>
    </Card>
  );
}
```

---

## 📱 **Fase 5: Páginas y Navegación**
*Tiempo estimado: 2-3 días*

### **5.1 Página de Login**
```tsx
// pages/auth/LoginPage.tsx
import React from 'react';
import { Navigate, Link, useLocation } from 'react-router-dom';
import { Box, Typography, Paper, Link as MuiLink } from '@mui/material';
import { LoginForm } from '../../components/users/LoginForm';
import { useAuth } from '../../context/AuthContext';

export function LoginPage() {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  // Si ya está autenticado, redirigir al dashboard o página anterior
  if (isAuthenticated && !loading) {
    const from = location.state?.from?.pathname || '/dashboard';
    return <Navigate to={from} replace />;
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'grey.100',
        py: 4,
      }}
    >
      <Box sx={{ width: '100%', maxWidth: 400 }}>
        <LoginForm />
        
        <Paper sx={{ p: 2, mt: 2, textAlign: 'center' }}>
          <Typography variant="body2">
            ¿No tienes cuenta?{' '}
            <MuiLink component={Link} to="/register">
              Regístrate aquí
            </MuiLink>
          </Typography>
        </Paper>
      </Box>
    </Box>
  );
}
```

### **5.2 Página de Registro**
```tsx
// pages/auth/RegisterPage.tsx
import React from 'react';
import { Navigate, Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
  Box,
  Button,
  TextField,
  Typography,
  Alert,
  Paper,
  CircularProgress,
  Link as MuiLink,
  Grid,
} from '@mui/material';
import { useAuth } from '../../context/AuthContext';
import { authService } from '../../services/authService';

const registerSchema = z.object({
  username: z.string()
    .min(3, 'El usuario debe tener al menos 3 caracteres')
    .max(30, 'El usuario no puede tener más de 30 caracteres'),
  email: z.string().email('Email inválido'),
  password: z.string()
    .min(8, 'La contraseña debe tener al menos 8 caracteres'),
  password_confirm: z.string(),
  first_name: z.string().max(30, 'Máximo 30 caracteres').optional(),
  last_name: z.string().max(30, 'Máximo 30 caracteres').optional(),
}).refine((data) => data.password === data.password_confirm, {
  message: "Las contraseñas no coinciden",
  path: ["password_confirm"],
});

type RegisterFormData = z.infer<typeof registerSchema>;

export function RegisterPage() {
  const { isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = React.useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [success, setSuccess] = React.useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  // Si ya está autenticado, redirigir al dashboard
  if (isAuthenticated && !loading) {
    return <Navigate to="/dashboard" replace />;
  }

  const onSubmit = async (data: RegisterFormData) => {
    setIsSubmitting(true);
    setError(null);
    
    try {
      await authService.register(data);
      setSuccess(true);
      setTimeout(() => {
        navigate('/login', { 
          state: { message: 'Registro exitoso. Ahora puedes iniciar sesión.' }
        });
      }, 2000);
    } catch (err: any) {
      if (err.response?.data) {
        const errorData = err.response.data;
        if (typeof errorData === 'object') {
          // Manejar errores específicos del backend
          const errorMessages = Object.values(errorData).flat().join(', ');
          setError(errorMessages);
        } else {
          setError(errorData.message || 'Error al registrar usuario');
        }
      } else {
        setError('Error de conexión. Intenta nuevamente.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (success) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'grey.100',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, maxWidth: 400, textAlign: 'center' }}>
          <Typography variant="h5" color="success.main" gutterBottom>
            ¡Registro Exitoso!
          </Typography>
          <Typography variant="body1">
            Tu cuenta ha sido creada. Serás redirigido al login...
          </Typography>
        </Paper>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'grey.100',
        py: 4,
      }}
    >
      <Paper elevation={3} sx={{ p: 4, maxWidth: 500, width: '100%' }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Crear Cuenta
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ mt: 1 }}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                {...register('username')}
                required
                fullWidth
                label="Nombre de Usuario"
                autoComplete="username"
                autoFocus
                error={!!errors.username}
                helperText={errors.username?.message}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                {...register('email')}
                required
                fullWidth
                label="Email"
                type="email"
                autoComplete="email"
                error={!!errors.email}
                helperText={errors.email?.message}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                {...register('first_name')}
                fullWidth
                label="Nombre"
                autoComplete="given-name"
                error={!!errors.first_name}
                helperText={errors.first_name?.message}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                {...register('last_name')}
                fullWidth
                label="Apellido"
                autoComplete="family-name"
                error={!!errors.last_name}
                helperText={errors.last_name?.message}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                {...register('password')}
                required
                fullWidth
                label="Contraseña"
                type="password"
                autoComplete="new-password"
                error={!!errors.password}
                helperText={errors.password?.message}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                {...register('password_confirm')}
                required
                fullWidth
                label="Confirmar Contraseña"
                type="password"
                autoComplete="new-password"
                error={!!errors.password_confirm}
                helperText={errors.password_confirm?.message}
              />
            </Grid>
          </Grid>
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={isSubmitting}
          >
            {isSubmitting ? <CircularProgress size={24} /> : 'Registrarse'}
          </Button>
        </Box>

        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Typography variant="body2">
            ¿Ya tienes cuenta?{' '}
            <MuiLink component={Link} to="/login">
              Inicia sesión aquí
            </MuiLink>
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
}
```

### **5.3 Layout Principal**
```tsx
// components/common/Layout.tsx
import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  AccountCircle,
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Description as DescriptionIcon,
  ExitToApp as LogoutIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const drawerWidth = 240;

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
    handleMenuClose();
  };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Contratos', icon: <DescriptionIcon />, path: '/contracts' },
    ...(user?.is_staff ? [
      { text: 'Usuarios', icon: <PeopleIcon />, path: '/users' },
    ] : []),
  ];

  const drawer = (
    <Box>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Contract Analysis
        </Typography>
      </Toolbar>
      <List>
        {menuItems.map((item) => (
          <ListItem
            key={item.text}
            button
            onClick={() => {
              navigate(item.path);
              if (isMobile) setMobileOpen(false);
            }}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setMobileOpen(!mobileOpen)}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Sistema de Análisis de Contratos
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2">
              {user?.first_name} {user?.last_name}
            </Typography>
            <IconButton
              size="large"
              onClick={handleProfileMenuOpen}
              color="inherit"
            >
              <Avatar src={user?.profile?.avatar} sx={{ width: 32, height: 32 }}>
                <AccountCircle />
              </Avatar>
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          mt: 8,
        }}
      >
        {children}
      </Box>

      {/* Profile Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        onClick={handleMenuClose}
      >
        <MenuItem onClick={() => navigate('/profile')}>
          <AccountCircle sx={{ mr: 1 }} />
          Mi Perfil
        </MenuItem>
        <MenuItem onClick={handleLogout}>
          <LogoutIcon sx={{ mr: 1 }} />
          Cerrar Sesión
        </MenuItem>
      </Menu>
    </Box>
  );
}
```

### **5.2 Página de Gestión de Usuarios**
```tsx
// pages/users/UsersManagementPage.tsx
import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  Paper,
  Pagination,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import { UserList } from '../../components/users/UserList';
import { UserForm } from '../../components/users/UserForm';
import { useUsers } from '../../hooks/useUsers';
import { User } from '../../types/user.types';

export function UsersManagementPage() {
  const { users, loading, pagination, fetchUsers } = useUsers();
  const [searchTerm, setSearchTerm] = useState('');
  const [userFormOpen, setUserFormOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setSearchTerm(value);
    
    // Debounce search
    const timeoutId = setTimeout(() => {
      fetchUsers(1, value);
    }, 500);
    
    return () => clearTimeout(timeoutId);
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, page: number) => {
    fetchUsers(page, searchTerm);
  };

  const handleAddUser = () => {
    setEditingUser(null);
    setUserFormOpen(true);
  };

  const handleEditUser = (user: User) => {
    setEditingUser(user);
    setUserFormOpen(true);
  };

  const handleCloseForm = () => {
    setUserFormOpen(false);
    setEditingUser(null);
  };

  const handleUserSaved = () => {
    fetchUsers(pagination.currentPage, searchTerm);
    handleCloseForm();
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Gestión de Usuarios
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddUser}
        >
          Nuevo Usuario
        </Button>
      </Box>

      {/* Search and Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <TextField
          placeholder="Buscar usuarios..."
          value={searchTerm}
          onChange={handleSearch}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ maxWidth: 400 }}
        />
      </Paper>

      {/* Users List */}
      <UserList onEditUser={handleEditUser} />

      {/* Pagination */}
      {pagination.count > 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Pagination
            count={Math.ceil(pagination.count / 10)}
            page={pagination.currentPage}
            onChange={handlePageChange}
            color="primary"
          />
        </Box>
      )}

      {/* User Form Dialog */}
      <Dialog
        open={userFormOpen}
        onClose={handleCloseForm}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingUser ? 'Editar Usuario' : 'Nuevo Usuario'}
        </DialogTitle>
        <DialogContent>
          <UserForm
            user={editingUser}
            onSave={handleUserSaved}
            onCancel={handleCloseForm}
          />
        </DialogContent>
      </Dialog>
    </Box>
  );
}
```

---

## 🔒 **Fase 6: Seguridad y Permisos**
*Tiempo estimado: 2 días*

### **6.1 Protected Routes**
```tsx
// components/common/ProtectedRoute.tsx
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { CircularProgress, Box } from '@mui/material';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
}

export function ProtectedRoute({ children, requireAdmin = false }: ProtectedRouteProps) {
  const { user, loading, isAuthenticated } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requireAdmin && !user?.is_staff) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}
```

### **6.2 App Principal con Rutas**
```tsx
// App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, CircularProgress } from '@mui/material';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Layout } from './components/common/Layout';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { Dashboard } from './pages/Dashboard';
import { ProfilePage } from './pages/users/ProfilePage';
import { UsersManagementPage } from './pages/users/UsersManagementPage';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

// Componente para mostrar loading mientras se verifica auth
function AuthLoader({ children }: { children: React.ReactNode }) {
  const { loading } = useAuth();
  
  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }
  
  return <>{children}</>;
}

// Componente principal de rutas
function AppRoutes() {
  return (
    <Routes>
      {/* Rutas públicas */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      
      {/* Rutas protegidas con Layout */}
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/profile" element={<ProfilePage />} />
                
                {/* Rutas de administrador */}
                <Route
                  path="/users"
                  element={
                    <ProtectedRoute requireAdmin>
                      <UsersManagementPage />
                    </ProtectedRoute>
                  }
                />
                
                {/* Redirect raíz a dashboard */}
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                
                {/* Página 404 para rutas no encontradas */}
                <Route 
                  path="*" 
                  element={<Navigate to="/dashboard" replace />} 
                />
              </Routes>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AuthProvider>
          <Router>
            <AuthLoader>
              <AppRoutes />
            </AuthLoader>
          </Router>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
```

---

## 🧪 **Fase 7: Testing y Optimización**
*Tiempo estimado: 3-4 días*

### **7.1 Environment Configuration**
```typescript
// .env.local
REACT_APP_API_URL=http://172.245.214.69/api
REACT_APP_WS_URL=ws://172.245.214.69/ws
REACT_APP_ENV=development

// .env.production
REACT_APP_API_URL=http://172.245.214.69/api
REACT_APP_WS_URL=ws://172.245.214.69/ws
REACT_APP_ENV=production
```

### **7.2 Error Boundaries**
```tsx
// components/common/ErrorBoundary.tsx
import React from 'react';
import { Alert, AlertTitle, Button, Box } from '@mui/material';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<
  React.PropsWithChildren<{}>,
  ErrorBoundaryState
> {
  constructor(props: React.PropsWithChildren<{}>) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ p: 3 }}>
          <Alert severity="error">
            <AlertTitle>¡Oops! Algo salió mal</AlertTitle>
            Ha ocurrido un error inesperado. Por favor, recarga la página.
            <Box sx={{ mt: 2 }}>
              <Button
                variant="outlined"
                onClick={() => window.location.reload()}
              >
                Recargar Página
              </Button>
            </Box>
          </Alert>
        </Box>
      );
    }

    return this.props.children;
  }
}
```

---

## 📋 **Cronograma de Implementación**

| Fase | Descripción | Tiempo | Dependencias |
|------|-------------|---------|--------------|
| **Fase 1** | Setup y Configuración Base | 3-4 días | - |
| **Fase 2** | Sistema de Autenticación | 2-3 días | Fase 1 |
| **Fase 3** | CRUD de Usuarios | 4-5 días | Fase 2 |
| **Fase 4** | Componentes de UI | 5-6 días | Fase 3 |
| **Fase 5** | Páginas y Navegación | 2-3 días | Fase 4 |
| **Fase 6** | Seguridad y Permisos | 2 días | Fase 5 |
| **Fase 7** | Testing y Optimización | 3-4 días | Todas |

**Tiempo Total Estimado: 21-28 días**

---

## 🎯 **Entregables**

### **MVP (Mínimo Producto Viable)**
- ✅ Login/Logout con JWT
- ✅ Registro de usuarios
- ✅ Perfil de usuario (ver/editar)
- ✅ Cambio de contraseña
- ✅ Lista de usuarios (admin)
- ✅ CRUD básico de usuarios (admin)

### **Características Avanzadas**
- 🔄 Upload de avatar
- 🔄 Gestión de roles y permisos
- 🔄 Búsqueda y filtros avanzados
- 🔄 Notificaciones en tiempo real
- 🔄 Auditoría de actividades

---

## 🚀 **Comandos de Desarrollo**

```bash
# Instalar dependencias
npm install

# Desarrollo
npm start

# Build para producción
npm run build

# Tests
npm test

# Linting
npm run lint
```

---

## 🔧 **Consideraciones Técnicas**

### **Performance**
- Lazy loading de componentes
- Memoización con React.memo
- Paginación en listas grandes
- Optimistic updates

### **UX/UI**
- Loading states consistentes
- Error handling amigable
- Feedback visual inmediato
- Responsive design

### **Seguridad**
- Validación en frontend y backend
- Sanitización de inputs
- Token refresh automático
- Timeout de sesión

---

## 📝 **Próximos Pasos**

1. **Revisar endpoints del backend** ✅ (Ya funcionando)
2. **Setup inicial del proyecto React**
3. **Implementar autenticación JWT**
4. **Desarrollar componentes de usuario**
5. **Integrar con sistema de contratos existente**
6. **Testing y deployment**

¿Te gustaría que comience con alguna fase específica o necesitas ajustes en la planificación?
