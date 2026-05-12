---
name: gestio-usuaris-admin
description: Disseny de la pàgina de gestió d'usuaris per a admins, incloent CRUD complet, model is_admin, i canvi de AbstractUser a AbstractBaseUser per eliminar is_staff/is_superuser/groups/user_permissions de la BD. Es conserven first_name, last_name, date_joined.
metadata:
  type: project
---

# Disseny: Gestió d'Usuaris (Admin) — DomusGestor

## Context

L'aplicació no tenia cap sistema de rols. Els usuaris s'autenticaven amb NIP+password i tots tenien el mateix accés. Cal afegir:
- Un camp `is_admin` per diferenciar admins d'usuaris normals.
- Una pàgina "Gestió" (només admins) amb CRUD complet d'usuaris.
- Eliminació de `is_staff`, `is_superuser`, `groups` i `user_permissions` de la BD (camps de Django no usats).
- Es conserven `first_name`, `last_name` i `date_joined` (aquest últim s'usa per ordenar usuaris per data de creació i mostrar-se a la taula de gestió).

---

## 1. Backend — Model `Usuari`

### Canvi de base: `AbstractUser` → `AbstractBaseUser`

Per eliminar `is_staff` i `is_superuser` completament de la BD (no estan en `AbstractBaseUser`), el model `Usuari` passa a heretar de `AbstractBaseUser`.

**Nou model:**
```python
class Usuari(AbstractBaseUser):
    username    = CharField(max_length=150, unique=True)
    first_name  = CharField(max_length=150, blank=True)
    last_name   = CharField(max_length=150, blank=True)
    email       = EmailField(unique=True)
    nip         = CharField(max_length=20, unique=True)
    is_active   = BooleanField(default=True)
    is_admin    = BooleanField(default=False)
    date_joined = DateTimeField(default=timezone.now)

    USERNAME_FIELD  = 'nip'
    REQUIRED_FIELDS = ['username', 'email']

    objects = UsuariManager()
```

**Camps eliminats de la BD:** `is_staff`, `is_superuser`, `groups`, `user_permissions`.

**Camps conservats:** `first_name`, `last_name`, `date_joined` (data de creació, usada per ordenar).

**Camps que queden de `AbstractBaseUser`:** `password`, `last_login`.

### `UsuariManager`
```python
class UsuariManager(BaseUserManager):
    def create_user(self, nip, username, email, password, **extra):
        user = self.model(nip=nip, username=username, email=email, **extra)
        user.set_password(password)
        user.save()
        return user
```

### Migració
Nova migració que recrea la taula `users_usuari` eliminant `is_staff`, `is_superuser`, `groups` i `user_permissions`. Conserva `first_name`, `last_name`, `date_joined`. Afegeix `is_admin`. Migra les dades existents.

---

## 2. Backend — Serialitzadors

### `UsuariSerializer` (ampliat)
Camps exposats: `id`, `username`, `first_name`, `last_name`, `email`, `nip`, `is_admin`, `is_active`, `date_joined`.
`is_active` i `date_joined` són read-only (el primer es gestiona per patch; el segon s'assigna automàticament).

### `CreateUsuariSerializer`
Camps: `username`, `first_name`, `last_name`, `email`, `nip`, `password` (write-only, min 6 chars), `is_admin`.

---

## 3. Backend — Permisos

```python
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
```

---

## 4. Backend — Endpoints nous

Prefix: `/api/auth/users/`

| Mètode | URL | Acció | Accés |
|--------|-----|-------|-------|
| GET    | `/api/auth/users/` | Llistar tots els usuaris | admin |
| POST   | `/api/auth/users/` | Crear usuari | admin |
| GET    | `/api/auth/users/<id>/` | Detall usuari | admin |
| PUT    | `/api/auth/users/<id>/` | Editar usuari (sense password) | admin |
| PATCH  | `/api/auth/users/<id>/` | Actualització parcial (ex: `is_active`) | admin |
| DELETE | `/api/auth/users/<id>/` | Eliminar usuari | admin |

**Regla de seguretat backend:** Un admin no pot deshabilitar ni eliminar el seu propi compte (`request.user.id == pk` → 403).

### `/api/auth/login/` i `/api/auth/me/`
Ja retornaran `is_admin` i `is_active` automàticament via el `UsuariSerializer` ampliat.

---

## 5. Frontend — Auth Context

`useAuth()` exposarà:
```js
isAdmin: user?.is_admin ?? false
```

No cal cap altre canvi estructural.

---

## 6. Frontend — Navegació (Header)

S'afegeix "Gestió" com a `NavLink` a la dreta de "Reserves", condicionat a `isAdmin`:

```jsx
{isAdmin && <NavLink to="/gestio">Gestió</NavLink>}
```

---

## 7. Frontend — Ruta `/gestio`

Ruta protegida: si `!isAdmin` → redirigeix a `/dashboard`.
Component: `GestioPage`.

---

## 8. Frontend — `GestioPage`

### Estructura
- Títol "Gestió d'usuaris" + botó "Nou usuari" (obre modal de creació)
- Taula amb columnes: **NIP**, **Nom d'usuari**, **Email**, **Admin**, **Estat**, **Data alta**, **Accions**
- Ordenació per defecte: `date_joined` descendent (usuari més nou a dalt)
- Fila activa (`is_active=true`): botó **Deshabilitar**
- Fila inactiva (`is_active=false`): botons **Habilitar** + **Eliminar**
- Botó **Editar** a totes les files (excepto la pròpia)
- La fila de l'usuari autenticat mostra "Tu" a la columna Estat i té els botons d'acció desactivats

### Modals de confirmació (reutilitzen estil de `Sidebar.jsx`)
- **Deshabilitar**: "Estàs segur que vols deshabilitar aquest usuari? L'usuari deixarà d'estar actiu."
- **Habilitar**: "Estàs segur que vols habilitar aquest usuari? L'usuari tornarà a estar actiu."
- **Eliminar**: "Estàs segur que vols eliminar aquest usuari? Aquesta acció és irreversible i s'eliminaran totes les dades associades."
- **Crear/Editar**: modal amb formulari (camps: username, first_name, last_name, email, nip, is_admin, password [només crear])

### Flux deshabilitar/eliminar
```
Usuari actiu → [Deshabilitar] → modal → PATCH is_active=false
Usuari inactiu → [Habilitar] → modal → PATCH is_active=true
Usuari inactiu → [Eliminar] → modal → DELETE
```
No es pot eliminar un usuari actiu directament.

---

## 9. Frontend — `api.js`

Nou `usersApi`:
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

---

## 10. Arxius afectats

### Backend
- `backend/users/models.py` — canvi a AbstractBaseUser, afegir is_admin
- `backend/users/serializers.py` — ampliar UsuariSerializer, afegir CreateUsuariSerializer
- `backend/users/views.py` — afegir UserListCreateView, UserDetailView, IsAdmin permission
- `backend/users/urls.py` — afegir rutes /users/
- `backend/users/migrations/000X_abstractbaseuser_is_admin.py` — nova migració

### Frontend
- `frontend/src/app/authContext.jsx` — exposar isAdmin
- `frontend/src/components/layout/Header.jsx` — afegir NavLink Gestió condicional
- `frontend/src/app/router.jsx` — afegir ruta /gestio
- `frontend/src/components/pages/GestioPage.jsx` — nova pàgina (+ .module.css)
- `frontend/src/services/api.js` — afegir usersApi
