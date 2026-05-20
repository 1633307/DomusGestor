# Gestió d'Usuaris Admin — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Afegir un sistema de rols (is_admin) i una pàgina de gestió d'usuaris completa accessible únicament per administradors.

**Architecture:** Switch del model `Usuari` de `AbstractUser` a `AbstractBaseUser` per eliminar `is_staff`, `is_superuser`, `groups` i `user_permissions` de la BD. Nous endpoints CRUD `/api/auth/users/` protegits per un permission class `IsAdmin`. Nova pàgina React `/gestio` amb taula + modals reutilitzant els estils de `Sidebar.jsx`.

**Tech Stack:** Django 5 + DRF (backend), React + Vite + CSS Modules (frontend), PostgreSQL.

---

## File Map

| Acció | Arxiu |
|-------|-------|
| Modify | `backend/users/models.py` |
| Auto-generate | `backend/users/migrations/0003_*.py` |
| Modify | `backend/users/serializers.py` |
| Modify | `backend/users/views.py` |
| Modify | `backend/users/urls.py` |
| Modify | `frontend/src/app/authContext.jsx` |
| Modify | `frontend/src/services/api.js` |
| Modify | `frontend/src/components/layout/Header.jsx` |
| Modify | `frontend/src/app/router.jsx` |
| Create | `frontend/src/components/pages/GestioPage.jsx` |
| Create | `frontend/src/components/pages/GestioPage.module.css` |

---

## Task 1: Backend — Model Usuari (AbstractBaseUser)

**Files:**
- Modify: `backend/users/models.py`

- [ ] **Step 1: Reescriure models.py**

Substituir el contingut complet de `backend/users/models.py` per:

```python
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UsuariManager(BaseUserManager):
    def create_user(self, nip, username, email, password, **extra_fields):
        if not nip:
            raise ValueError('El NIP és obligatori')
        email = self.normalize_email(email)
        user = self.model(nip=nip, username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class Usuari(AbstractBaseUser):
    username    = models.CharField(max_length=150, unique=True)
    first_name  = models.CharField(max_length=150, blank=True)
    last_name   = models.CharField(max_length=150, blank=True)
    email       = models.EmailField(unique=True)
    nip         = models.CharField(
        max_length=20, unique=True,
        verbose_name="NIP (Número d'Identificació Personal)"
    )
    is_active   = models.BooleanField(default=True)
    is_admin    = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD  = 'nip'
    REQUIRED_FIELDS = ['username', 'email']

    objects = UsuariManager()

    def __str__(self):
        return self.username


class InfoImmobiliaria(models.Model):
    nom_comercial   = models.CharField(max_length=100)
    cif             = models.CharField(max_length=20, unique=True)
    adreca          = models.TextField()
    email_contacte  = models.EmailField()
    telefon         = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Informació General Immobiliària"

    def __str__(self):
        return self.nom_comercial
```

- [ ] **Step 2: Generar la migració**

Des de `backend/`:
```
python manage.py makemigrations users
```

Resultat esperat: Django genera `backend/users/migrations/0003_<nom>.py` amb operacions:
- `RemoveField(model_name='usuari', name='groups')`
- `RemoveField(model_name='usuari', name='user_permissions')`
- `RemoveField(model_name='usuari', name='is_staff')`
- `RemoveField(model_name='usuari', name='is_superuser')`
- `AddField(model_name='usuari', name='is_admin', field=BooleanField(default=False))`

- [ ] **Step 3: Aplicar la migració**

```
python manage.py migrate
```

Resultat esperat: `Applying users.0003_... OK`

- [ ] **Step 4: Verificar que el servidor arrenca sense errors**

```
python manage.py runserver
```

Resultat esperat: servidor arrenca sense `ImproperlyConfigured` ni errors de migració.

- [ ] **Step 5: Commit**

```bash
git add backend/users/models.py backend/users/migrations/
git commit -m "feat: switch Usuari to AbstractBaseUser, add is_admin, remove is_staff/is_superuser/groups/user_permissions"
```

---

## Task 2: Backend — Serialitzadors

**Files:**
- Modify: `backend/users/serializers.py`

- [ ] **Step 1: Reescriure serializers.py**

Substituir el contingut complet de `backend/users/serializers.py` per:

```python
from rest_framework import serializers
from .models import Usuari, InfoImmobiliaria


class LoginSerializer(serializers.Serializer):
    nip      = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = Usuari.objects.get(nip=data['nip'])
        except Usuari.DoesNotExist:
            raise serializers.ValidationError('Credencials incorrectes.')

        if not user.check_password(data['password']):
            raise serializers.ValidationError('Credencials incorrectes.')

        if not user.is_active:
            raise serializers.ValidationError('Compte desactivat.')

        data['user'] = user
        return data


class UsuariSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Usuari
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'nip', 'is_admin', 'is_active', 'date_joined',
        ]
        read_only_fields = ['id', 'date_joined']


class CreateUsuariSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model  = Usuari
        fields = ['username', 'first_name', 'last_name', 'email', 'nip', 'password', 'is_admin']

    def validate_nip(self, value):
        if Usuari.objects.filter(nip=value).exists():
            raise serializers.ValidationError("Ja existeix un usuari amb aquest NIP.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuari(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UpdateUsuariSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Usuari
        fields = ['username', 'first_name', 'last_name', 'email', 'nip', 'is_admin']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model  = Usuari
        fields = ['username', 'email', 'nip', 'password']

    def validate_nip(self, value):
        if Usuari.objects.filter(nip=value).exists():
            raise serializers.ValidationError("Ja existeix un usuari amb aquest NIP.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuari(**validated_data)
        user.set_password(password)
        user.save()
        return user


class InfoImmobiliariaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = InfoImmobiliaria
        fields = '__all__'
```

- [ ] **Step 2: Verificar que el servidor segueix arrencant**

```
python manage.py runserver
```

Resultat esperat: sense errors d'importació.

- [ ] **Step 3: Commit**

```bash
git add backend/users/serializers.py
git commit -m "feat: update serializers - add UsuariSerializer with is_admin/date_joined, add CreateUsuariSerializer and UpdateUsuariSerializer"
```

---

## Task 3: Backend — Permission class + Views CRUD + URLs

**Files:**
- Modify: `backend/users/views.py`
- Modify: `backend/users/urls.py`

- [ ] **Step 1: Reescriure views.py**

Substituir el contingut complet de `backend/users/views.py` per:

```python
from django.http import Http404
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Usuari, InfoImmobiliaria
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UsuariSerializer,
    CreateUsuariSerializer,
    UpdateUsuariSerializer,
    InfoImmobiliariaSerializer,
)


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_admin
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user  = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UsuariSerializer(user).data})


class LogoutView(APIView):
    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterView(generics.CreateAPIView):
    serializer_class   = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user  = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {'token': token.key, 'user': UsuariSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    def get(self, request):
        return Response(UsuariSerializer(request.user).data)


class UserListCreateView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        users = Usuari.objects.all().order_by('-date_joined')
        return Response(UsuariSerializer(users, many=True).data)

    def post(self, request):
        serializer = CreateUsuariSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UsuariSerializer(user).data, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    permission_classes = [IsAdmin]

    def get_object(self, pk):
        try:
            return Usuari.objects.get(pk=pk)
        except Usuari.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        return Response(UsuariSerializer(self.get_object(pk)).data)

    def put(self, request, pk):
        user = self.get_object(pk)
        serializer = UpdateUsuariSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UsuariSerializer(user).data)

    def patch(self, request, pk):
        user = self.get_object(pk)
        is_active = request.data.get('is_active')
        if is_active is not None:
            if not is_active and request.user.pk == pk:
                return Response(
                    {'detail': 'No pots deshabilitar el teu propi compte.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            user.is_active = bool(is_active)
            user.save(update_fields=['is_active'])
        return Response(UsuariSerializer(user).data)

    def delete(self, request, pk):
        if request.user.pk == pk:
            return Response(
                {'detail': 'No pots eliminar el teu propi compte.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        user = self.get_object(pk)
        if user.is_active:
            return Response(
                {'detail': "Has de deshabilitar l'usuari abans d'eliminar-lo."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InfoImmobiliariaListCreateView(generics.ListCreateAPIView):
    queryset           = InfoImmobiliaria.objects.all()
    serializer_class   = InfoImmobiliariaSerializer


class InfoImmobiliariaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = InfoImmobiliaria.objects.all()
    serializer_class   = InfoImmobiliariaSerializer
```

- [ ] **Step 2: Actualitzar urls.py**

Substituir el contingut de `backend/users/urls.py` per:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('login/',    views.LoginView.as_view(),    name='login'),
    path('logout/',   views.LogoutView.as_view(),   name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('me/',       views.MeView.as_view(),       name='me'),
    path('users/',             views.UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/',    views.UserDetailView.as_view(),     name='user-detail'),
    path('info-immobiliaria/',          views.InfoImmobiliariaListCreateView.as_view(), name='info-immobiliaria-list'),
    path('info-immobiliaria/<int:pk>/', views.InfoImmobiliariaDetailView.as_view(),     name='info-immobiliaria-detail'),
]
```

- [ ] **Step 3: Verificar endpoints amb curl**

Necessites un token d'admin. Primer fes login:
```
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"nip":"<NIP_ADMIN>","password":"<PASSWORD>"}'
```
Copia el token. Després:
```
curl http://localhost:8000/api/auth/users/ \
  -H "Authorization: Token <TOKEN>"
```
Resultat esperat: llista JSON d'usuaris amb camps `id, username, first_name, last_name, email, nip, is_admin, is_active, date_joined`.

Prova de seguretat (sense token):
```
curl http://localhost:8000/api/auth/users/
```
Resultat esperat: `{"detail":"Authentication credentials were not provided."}`

- [ ] **Step 4: Activar el primer admin**

Si no tens cap usuari amb `is_admin=True`, fes-ho des de la shell de Django:
```
python manage.py shell
>>> from users.models import Usuari
>>> u = Usuari.objects.get(nip='<NIP>')
>>> u.is_admin = True
>>> u.save()
```

- [ ] **Step 5: Commit**

```bash
git add backend/users/views.py backend/users/urls.py
git commit -m "feat: add IsAdmin permission, UserListCreateView, UserDetailView and CRUD urls"
```

---

## Task 4: Frontend — authContext + api.js

**Files:**
- Modify: `frontend/src/app/authContext.jsx`
- Modify: `frontend/src/services/api.js`

- [ ] **Step 1: Afegir isAdmin a authContext.jsx**

Localitza el `useMemo` a `frontend/src/app/authContext.jsx` (línia 42) i substitueix-lo per:

```jsx
const value = useMemo(
  () => ({
    user,
    isAuthenticated: Boolean(user),
    isAdmin: user?.is_admin ?? false,
    loading,
    login,
    logout,
  }),
  [user, loading]
);
```

- [ ] **Step 2: Afegir usersApi a api.js**

Afegir al final de `frontend/src/services/api.js`:

```js
export const usersApi = {
  list:   ()         => api.get('/auth/users/'),
  get:    (id)       => api.get(`/auth/users/${id}/`),
  create: (data)     => api.post('/auth/users/', data),
  update: (id, data) => api.put(`/auth/users/${id}/`, data),
  patch:  (id, data) => api.patch(`/auth/users/${id}/`, data),
  remove: (id)       => api.del(`/auth/users/${id}/`),
};
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/authContext.jsx frontend/src/services/api.js
git commit -m "feat: expose isAdmin from authContext, add usersApi"
```

---

## Task 5: Frontend — Header (nav Gestió)

**Files:**
- Modify: `frontend/src/components/layout/Header.jsx`

- [ ] **Step 1: Actualitzar Header.jsx**

Substituir el contingut complet de `frontend/src/components/layout/Header.jsx` per:

```jsx
import { useAuth } from '../../app/authContext';
import { NavLink } from 'react-router-dom';
import styles from './Header.module.css';

export default function Header() {
  const { user, logout, isAdmin } = useAuth();

  return (
    <header className={styles.header}>
      <div class="col1">
        <h1 className={styles.title}>Domus Gestor</h1>
      </div>

      <div class="col2" className={styles.headerActions}>
        <span>{user?.username || 'Usuari'}</span>
        <button className={styles.secondaryButton} onClick={logout}>
          Cerrar sesión
        </button>
      </div>

      <div class="fila">
        <nav className={styles.sidebarNav}>
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              isActive ? `${styles.link} ${styles.activeLink}` : styles.link
            }
          >
            Dashboard
          </NavLink>

          <NavLink
            to="/properties"
            className={({ isActive }) =>
              isActive ? `${styles.link} ${styles.activeLink}` : styles.link
            }
          >
            Cercador
          </NavLink>

          <NavLink
            to="/inmobles"
            className={({ isActive }) =>
              isActive ? `${styles.link} ${styles.activeLink}` : styles.link
            }
          >
            Immobles
          </NavLink>

          <NavLink
            to="/reserves"
            className={({ isActive }) =>
              isActive ? `${styles.link} ${styles.activeLink}` : styles.link
            }
          >
            Reserves
          </NavLink>

          {isAdmin && (
            <NavLink
              to="/gestio"
              className={({ isActive }) =>
                isActive ? `${styles.link} ${styles.activeLink}` : styles.link
              }
            >
              Gestió
            </NavLink>
          )}
        </nav>
      </div>
    </header>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/layout/Header.jsx
git commit -m "feat: add Gestio nav link visible only for admin users"
```

---

## Task 6: Frontend — Router + GestioPage

**Files:**
- Modify: `frontend/src/app/router.jsx`
- Create: `frontend/src/components/pages/GestioPage.jsx`
- Create: `frontend/src/components/pages/GestioPage.module.css`

- [ ] **Step 1: Afegir ruta a router.jsx**

Substituir el contingut complet de `frontend/src/app/router.jsx` per:

```jsx
import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./appLayout";
import ProtectedRoute from "../ProtectedRoute";
import LoginPage from "../components/pages/LoginPage";
import DashboardPage from "../components/pages/DashboardPage";
import CercadorPage from "../components/pages/CercadorPage";
import InmoblesPage from "../components/pages/InmoblesPage";
import InfoInmoble from "../components/pages/InfoInmoblePage";
import ReservesPage from "../components/pages/reservesPage";
import InfoReserva from "../components/pages/infoReservaPage";
import GestioPage from "../components/pages/GestioPage";

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="properties" element={<CercadorPage />} />
        <Route path="inmobles" element={<InmoblesPage />} />
        <Route path="reserves" element={<ReservesPage />} />
        <Route path="infoInmoble/:id" element={<InfoInmoble />} />
        <Route path="infoReserva/:id" element={<InfoReserva />} />
        <Route path="gestio" element={<GestioPage />} />
      </Route>
    </Routes>
  );
}
```

- [ ] **Step 2: Crear GestioPage.jsx**

Crear el fitxer `frontend/src/components/pages/GestioPage.jsx` amb el contingut:

```jsx
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../app/authContext";
import { usersApi } from "../../services/api";
import styles from "./GestioPage.module.css";

const emptyForm = {
  username: "",
  first_name: "",
  last_name: "",
  email: "",
  nip: "",
  is_admin: false,
  password: "",
};

export default function GestioPage() {
  const { user: currentUser, isAdmin } = useAuth();
  const navigate = useNavigate();

  const [users, setUsers]                     = useState([]);
  const [loading, setLoading]                 = useState(true);
  const [error, setError]                     = useState("");
  const [modalDeshabilitar, setModalDeshabilitar] = useState(null);
  const [modalHabilitar, setModalHabilitar]   = useState(null);
  const [modalEliminar, setModalEliminar]     = useState(null);
  const [modalForm, setModalForm]             = useState(null); // null | "create" | user object
  const [form, setForm]                       = useState(emptyForm);
  const [formError, setFormError]             = useState("");
  const [saving, setSaving]                   = useState(false);

  useEffect(() => {
    if (!isAdmin) {
      navigate("/dashboard");
      return;
    }
    loadUsers();
  }, [isAdmin]);

  const loadUsers = () => {
    setLoading(true);
    usersApi
      .list()
      .then((data) => setUsers(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  const handleDeshabilitar = async () => {
    try {
      await usersApi.patch(modalDeshabilitar.id, { is_active: false });
      setUsers((prev) =>
        prev.map((u) =>
          u.id === modalDeshabilitar.id ? { ...u, is_active: false } : u
        )
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setModalDeshabilitar(null);
    }
  };

  const handleHabilitar = async () => {
    try {
      await usersApi.patch(modalHabilitar.id, { is_active: true });
      setUsers((prev) =>
        prev.map((u) =>
          u.id === modalHabilitar.id ? { ...u, is_active: true } : u
        )
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setModalHabilitar(null);
    }
  };

  const handleEliminar = async () => {
    try {
      await usersApi.remove(modalEliminar.id);
      setUsers((prev) => prev.filter((u) => u.id !== modalEliminar.id));
    } catch (err) {
      setError(err.message);
    } finally {
      setModalEliminar(null);
    }
  };

  const openCreate = () => {
    setForm(emptyForm);
    setFormError("");
    setModalForm("create");
  };

  const openEdit = (u) => {
    setForm({
      username:   u.username,
      first_name: u.first_name || "",
      last_name:  u.last_name  || "",
      email:      u.email,
      nip:        u.nip,
      is_admin:   u.is_admin,
      password:   "",
    });
    setFormError("");
    setModalForm(u);
  };

  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
  };

  const handleFormSubmit = async () => {
    setSaving(true);
    setFormError("");
    try {
      if (modalForm === "create") {
        const created = await usersApi.create(form);
        setUsers((prev) => [created, ...prev]);
      } else {
        const { password, ...updateData } = form;
        const updated = await usersApi.update(modalForm.id, updateData);
        setUsers((prev) =>
          prev.map((u) => (u.id === modalForm.id ? updated : u))
        );
      }
      setModalForm(null);
    } catch (err) {
      if (err.fieldErrors) {
        const [field, msgs] = Object.entries(err.fieldErrors)[0];
        setFormError(`${field}: ${Array.isArray(msgs) ? msgs[0] : msgs}`);
      } else {
        setFormError(err.message);
      }
    } finally {
      setSaving(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "-";
    return new Date(dateStr).toLocaleDateString("ca-ES", {
      year: "numeric", month: "2-digit", day: "2-digit",
    });
  };

  if (loading) return <p>Carregant usuaris...</p>;

  return (
    <section className={styles.page}>
      <div className={styles.pageHeader}>
        <h2>Gestió d'usuaris</h2>
        <button className={styles.btnNou} onClick={openCreate}>
          Nou usuari
        </button>
      </div>

      {error && <p className={styles.error}>{error}</p>}

      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>NIP</th>
              <th>Nom d'usuari</th>
              <th>Email</th>
              <th>Admin</th>
              <th>Estat</th>
              <th>Data alta</th>
              <th>Accions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => {
              const isSelf = u.id === currentUser?.id;
              return (
                <tr key={u.id} className={!u.is_active ? styles.rowDisabled : ""}>
                  <td>{u.nip}</td>
                  <td>{u.username}</td>
                  <td>{u.email}</td>
                  <td>{u.is_admin ? "Sí" : "No"}</td>
                  <td>
                    {isSelf ? (
                      <span className={styles.badgeSelf}>Tu</span>
                    ) : u.is_active ? (
                      <span className={styles.badgeActiu}>Actiu</span>
                    ) : (
                      <span className={styles.badgeInactiu}>Inactiu</span>
                    )}
                  </td>
                  <td>{formatDate(u.date_joined)}</td>
                  <td className={styles.actions}>
                    {!isSelf && (
                      <>
                        <button
                          className={styles.btnEditar}
                          onClick={() => openEdit(u)}
                        >
                          Editar
                        </button>
                        {u.is_active ? (
                          <button
                            className={styles.btnDeshabilitar}
                            onClick={() => setModalDeshabilitar(u)}
                          >
                            Deshabilitar
                          </button>
                        ) : (
                          <>
                            <button
                              className={styles.btnHabilitar}
                              onClick={() => setModalHabilitar(u)}
                            >
                              Habilitar
                            </button>
                            <button
                              className={styles.btnEliminar}
                              onClick={() => setModalEliminar(u)}
                            >
                              Eliminar
                            </button>
                          </>
                        )}
                      </>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {modalDeshabilitar && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h3>Deshabilitar usuari</h3>
            <p>
              Estàs segur que vols deshabilitar{" "}
              <strong>{modalDeshabilitar.username}</strong>? L'usuari deixarà
              d'estar actiu.
            </p>
            <div className={styles.modalActions}>
              <button
                className={styles.btnCancel}
                onClick={() => setModalDeshabilitar(null)}
              >
                Cancel·lar
              </button>
              <button
                className={styles.btnConfirmDeshabilitar}
                onClick={handleDeshabilitar}
              >
                Deshabilitar
              </button>
            </div>
          </div>
        </div>
      )}

      {modalHabilitar && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h3>Habilitar usuari</h3>
            <p>
              Estàs segur que vols habilitar{" "}
              <strong>{modalHabilitar.username}</strong>? L'usuari tornarà a
              estar actiu.
            </p>
            <div className={styles.modalActions}>
              <button
                className={styles.btnCancel}
                onClick={() => setModalHabilitar(null)}
              >
                Cancel·lar
              </button>
              <button
                className={styles.btnConfirmHabilitar}
                onClick={handleHabilitar}
              >
                Habilitar
              </button>
            </div>
          </div>
        </div>
      )}

      {modalEliminar && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h3>Eliminar usuari</h3>
            <p>
              Estàs segur que vols eliminar{" "}
              <strong>{modalEliminar.username}</strong>? Aquesta acció és
              irreversible i s'eliminaran totes les dades associades.
            </p>
            <div className={styles.modalActions}>
              <button
                className={styles.btnCancel}
                onClick={() => setModalEliminar(null)}
              >
                Cancel·lar
              </button>
              <button
                className={styles.btnConfirmEliminar}
                onClick={handleEliminar}
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}

      {modalForm && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h3>{modalForm === "create" ? "Nou usuari" : "Editar usuari"}</h3>
            {formError && <p className={styles.formError}>{formError}</p>}
            <div className={styles.formGrid}>
              <label>
                NIP
                <input
                  name="nip"
                  value={form.nip}
                  onChange={handleFormChange}
                  autoComplete="off"
                />
              </label>
              <label>
                Nom d'usuari
                <input
                  name="username"
                  value={form.username}
                  onChange={handleFormChange}
                  autoComplete="off"
                />
              </label>
              <label>
                Nom
                <input
                  name="first_name"
                  value={form.first_name}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                Cognom
                <input
                  name="last_name"
                  value={form.last_name}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                Email
                <input
                  name="email"
                  type="email"
                  value={form.email}
                  onChange={handleFormChange}
                  autoComplete="off"
                />
              </label>
              {modalForm === "create" && (
                <label>
                  Contrasenya
                  <input
                    name="password"
                    type="password"
                    value={form.password}
                    onChange={handleFormChange}
                    autoComplete="new-password"
                  />
                </label>
              )}
              <label className={styles.checkboxLabel}>
                <input
                  name="is_admin"
                  type="checkbox"
                  checked={form.is_admin}
                  onChange={handleFormChange}
                />
                Administrador
              </label>
            </div>
            <div className={styles.modalActions}>
              <button
                className={styles.btnCancel}
                onClick={() => setModalForm(null)}
              >
                Cancel·lar
              </button>
              <button
                className={styles.btnConfirmHabilitar}
                onClick={handleFormSubmit}
                disabled={saving}
              >
                {saving ? "Guardant..." : "Guardar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
```

- [ ] **Step 3: Crear GestioPage.module.css**

Crear el fitxer `frontend/src/components/pages/GestioPage.module.css` amb el contingut:

```css
.page {
  padding: 32px 28px;
  max-width: 1100px;
}

.pageHeader {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.pageHeader h2 {
  margin: 0;
  font-size: 1.4rem;
  color: #1e293b;
}

.btnNou {
  padding: 9px 20px;
  border-radius: 10px;
  border: none;
  background: #2563eb;
  color: #fff;
  font: inherit;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btnNou:hover {
  background: #1d4ed8;
}

.error {
  color: #e11d48;
  margin-bottom: 16px;
  font-size: 0.9rem;
}

.tableWrapper {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.table th,
.table td {
  padding: 12px 14px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.table th {
  background: #f8fafc;
  color: #64748b;
  font-weight: 600;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.table tbody tr:hover {
  background: #f8fafc;
}

.rowDisabled td {
  color: #94a3b8;
}

.badgeActiu {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  background: #dcfce7;
  color: #16a34a;
  font-size: 0.8rem;
  font-weight: 600;
}

.badgeInactiu {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  background: #fee2e2;
  color: #dc2626;
  font-size: 0.8rem;
  font-weight: 600;
}

.badgeSelf {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  background: #dbeafe;
  color: #2563eb;
  font-size: 0.8rem;
  font-weight: 600;
}

.actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btnEditar {
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #475569;
  font: inherit;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btnEditar:hover {
  background: #e2e8f0;
}

.btnDeshabilitar {
  padding: 6px 12px;
  border-radius: 8px;
  border: none;
  background: #fee2e2;
  color: #dc2626;
  font: inherit;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btnDeshabilitar:hover {
  background: #fecaca;
}

.btnHabilitar {
  padding: 6px 12px;
  border-radius: 8px;
  border: none;
  background: #dbeafe;
  color: #1d4ed8;
  font: inherit;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btnHabilitar:hover {
  background: #bfdbfe;
}

.btnEliminar {
  padding: 6px 12px;
  border-radius: 8px;
  border: none;
  background: #ef4444;
  color: #fff;
  font: inherit;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btnEliminar:hover {
  background: #dc2626;
}

/* Modals — reutilitzen l'estil de Sidebar.module.css */
.modalOverlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #fff;
  border-radius: 14px;
  padding: 32px 28px;
  max-width: 480px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal h3 {
  margin: 0 0 12px;
  font-size: 1.2rem;
  color: #1e293b;
}

.modal p {
  margin: 0 0 24px;
  color: #475569;
  font-size: 0.95rem;
  line-height: 1.5;
}

.modalActions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btnCancel {
  padding: 9px 18px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #475569;
  font: inherit;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btnCancel:hover {
  background: #e2e8f0;
}

.btnConfirmDeshabilitar {
  padding: 9px 18px;
  border-radius: 8px;
  border: none;
  background: #ef4444;
  color: #fff;
  font: inherit;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btnConfirmDeshabilitar:hover {
  background: #dc2626;
}

.btnConfirmHabilitar {
  padding: 9px 18px;
  border-radius: 8px;
  border: none;
  background: #2563eb;
  color: #fff;
  font: inherit;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btnConfirmHabilitar:hover {
  background: #1d4ed8;
}

.btnConfirmEliminar {
  padding: 9px 18px;
  border-radius: 8px;
  border: none;
  background: #ef4444;
  color: #fff;
  font: inherit;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btnConfirmEliminar:hover {
  background: #dc2626;
}

/* Formulari crear/editar */
.formGrid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-bottom: 24px;
}

.formGrid label {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
}

.formGrid input[type="text"],
.formGrid input[type="email"],
.formGrid input[type="password"],
.formGrid input:not([type="checkbox"]) {
  padding: 8px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font: inherit;
  font-size: 0.9rem;
  color: #1e293b;
  background: #f8fafc;
  outline: none;
  transition: border-color 0.2s ease;
}

.formGrid input:not([type="checkbox"]):focus {
  border-color: #2563eb;
  background: #fff;
}

.checkboxLabel {
  flex-direction: row !important;
  align-items: center;
  gap: 8px !important;
  grid-column: 1 / -1;
}

.checkboxLabel input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.formError {
  color: #e11d48;
  font-size: 0.85rem;
  margin: 0 0 16px;
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/app/router.jsx frontend/src/components/pages/GestioPage.jsx frontend/src/components/pages/GestioPage.module.css
git commit -m "feat: add GestioPage with full user CRUD, disable/enable/delete modals"
```

---

## Verificació final

- [ ] Reinicia backend i frontend
- [ ] Login amb usuari admin → veure pestanya "Gestió" al header
- [ ] Login amb usuari normal → NO veure "Gestió"; accés manual a `/gestio` redirigeix a `/dashboard`
- [ ] Crear nou usuari des del modal → apareix a la taula
- [ ] Editar usuari → canvis reflectits
- [ ] Deshabilitar usuari → badge canvia a "Inactiu", botons canvien a Habilitar + Eliminar
- [ ] Habilitar usuari → badge torna a "Actiu"
- [ ] Eliminar usuari inactiu → desapareix de la taula
- [ ] Intentar deshabilitar/eliminar el propi compte → botons no apareixen (fila "Tu")
- [ ] El camp `date_joined` és visible i la taula ordena de més nou a més antic
