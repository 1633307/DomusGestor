# Frontend — Domus Gestor

Frontend de **Domus Gestor**, desarrollado con **React + Vite**.  
Esta parte del proyecto corresponde a la interfaz de usuario del sistema de gestión de alojamientos turísticos.

Actualmente el frontend ya incluye una base funcional con:

- pantalla de inicio de sesión
- sistema de rutas
- rutas protegidas
- layout general de aplicación
- dashboard inicial
- página de inmuebles
- formulario mock de alta de inmuebles

---

## Estado actual del proyecto

En este momento el frontend permite:

### Autenticación
- acceso mediante una pantalla de login
- autenticación simulada con `authContext`
- protección de rutas privadas

### Estructura general de la app
- sidebar lateral
- header superior
- zona central de contenido
- navegación entre páginas internas

### Dashboard
- pantalla de resumen general
- tarjetas base para futuras métricas

### Inmuebles
- listado mock de propiedades
- botón de nuevo inmueble
- formulario de creación
- inserción local del nuevo inmueble en la vista

⚠️ Importante:  
Por ahora todo funciona con datos mock y estado local.  
Todavía no existe conexión real con el backend.

---

## Tecnologías usadas

- React
- Vite
- JavaScript
- CSS
- React Router DOM

---

## Cómo ejecutar el proyecto

Desde la carpeta `frontend`:

```bash
npm install
npm install react-router-dom
npm run dev

Abrir en navegador:

http://localhost:5173/


Estructura actual
frontend/
│
├── public/
├── src/
│   ├── app/
│   │   ├── appLayout.jsx
│   │   └── router.jsx
│   │
│   ├── components/
│   │   └── layout/
│   │       ├── header.jsx
│   │       ├── protectedRoute.jsx
│   │       └── sidebar.jsx
│   │
│   ├── features/
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   │   └── loginForm.jsx
│   │   │   ├── pages/
│   │   │   │   └── loginPage.jsx
│   │   │   └── authContext.jsx
│   │   │
│   │   ├── dashboard/
│   │   │   └── pages/
│   │   │       └── dashboardPage.jsx
│   │   │
│   │   └── properties/
│   │       ├── components/
│   │       │   └── propertyForm.jsx
│   │       └── pages/
│   │           └── propertiesPage.jsx
│   │
│   ├── styles/
│   │   └── global.css
│   │
│   └── main.jsx
│
├── package.json
└── vite.config.js
Explicación de la estructura
src/main.jsx

Es el punto de entrada de toda la aplicación.

Se encarga de:

arrancar React
envolver la app con BrowserRouter
envolver la app con AuthProvider
cargar los estilos globales
renderizar el sistema de rutas definido en router.jsx
src/app/
router.jsx

Define la navegación principal de la aplicación.

Actualmente gestiona estas rutas:

/login
/dashboard
/properties

También se encarga de:

redirigir al login si no hay autenticación
envolver la parte privada con AppLayout
appLayout.jsx

Es la estructura base de la aplicación una vez el usuario ha iniciado sesión.

Contiene:

Sidebar
Header
Outlet para mostrar la página actual
src/components/layout/

Contiene componentes compartidos del layout general.

header.jsx

Cabecera superior del panel.
Muestra el nombre del sistema y permite cerrar sesión.

sidebar.jsx

Barra lateral de navegación.
Permite moverse entre el dashboard y la sección de inmuebles.

protectedRoute.jsx

Componente que protege rutas privadas.
Si el usuario no está autenticado, redirige a /login.

src/features/

Aquí se organiza el proyecto por funcionalidades.

Cada bloque importante del sistema vive dentro de su propia carpeta.
Esta estructura permite que el proyecto crezca sin mezclar archivos de distintas partes.

Actualmente existen estas features:

auth
dashboard
properties
Feature: Auth

Ruta:

src/features/auth/

Contiene todo lo relacionado con autenticación.

Archivos actuales
pages/loginPage.jsx

Página de inicio de sesión.

components/loginForm.jsx

Formulario del login.

authContext.jsx

Gestiona el estado global de autenticación.

Ahora mismo la autenticación es simulada:

cualquier NIP + contraseña válida no vacía permite entrar
no hay token
no hay API real
Feature: Dashboard

Ruta:

src/features/dashboard/
Archivos actuales
pages/dashboardPage.jsx

Primera pantalla que aparece tras iniciar sesión.

Muestra:

título de dashboard
subtítulo
tarjetas base de resumen

Esta pantalla sirve como estructura inicial y se ampliará más adelante con métricas reales.

Feature: Properties

Ruta:

src/features/properties/

Contiene la parte inicial de gestión de inmuebles.

Archivos actuales
pages/propertiesPage.jsx

Página principal de inmuebles.

Incluye:

título de sección
botón para crear nuevo inmueble
buscador visual
filtro visual
grid de tarjetas
listado mock de propiedades
apertura/cierre del formulario
components/propertyForm.jsx

Formulario base para crear un inmueble nuevo.

Campos actuales:

nombre
ciudad
dirección
capacidad
precio por noche
estado

Al guardar:

se crea un nuevo objeto
se añade al estado local
se muestra en el listado

⚠️ Todavía no guarda en backend.

Estilos

Ruta:

src/styles/global.css

Contiene todos los estilos globales del proyecto.

Actualmente incluye estilos para:

login
layout general
sidebar
header
dashboard
cards
página de inmuebles
formulario de inmuebles

Se está utilizando un estilo visual oscuro, limpio y sencillo, inspirado en la estética por defecto de React/Vite.

Convención actual del proyecto
Archivos

Los archivos se nombran en camelCase con inicial minúscula:

appLayout.jsx
loginPage.jsx
dashboardPage.jsx
propertyForm.jsx
Componentes React

Los componentes dentro del código se nombran en PascalCase:

AppLayout
LoginPage
DashboardPage
PropertyForm

Esto permite:

mantener nombres de archivo homogéneos
respetar la convención correcta de React para componentes
Cómo se organiza una nueva funcionalidad

Cada nueva funcionalidad debe crearse dentro de features/.

Estructura recomendada:

feature/
  components/
  pages/
  services/
  hooks/
  utils/
Uso recomendado de cada carpeta
pages/

Pantallas completas asociadas a rutas.

components/

Componentes reutilizables dentro de una feature.

services/

Lógica de acceso a backend o datos externos.

hooks/

Lógica reutilizable con hooks personalizados.

utils/

Funciones auxiliares.

Flujo actual de la aplicación

Actualmente el flujo principal es:

/login → autenticación mock → /dashboard

Desde dentro de la app:

el usuario ve AppLayout
puede navegar por Sidebar
puede acceder a Dashboard
puede acceder a Properties
Qué falta por implementar

Las siguientes mejoras previstas son:

Autenticación
conexión real con backend
gestión de sesión real
almacenamiento de token
Dashboard
métricas reales
cards con datos del sistema
accesos rápidos
Properties
buscador funcional
filtro funcional
edición de inmuebles
borrado de inmuebles
conexión con backend
Nuevas features futuras
reservas
inquilinos
propietarios
pagos
Orden recomendado de desarrollo a partir de ahora
subir y consolidar esta base
hacer funcional el buscador/filtro de inmuebles
reutilizar propertyForm para editar
separar datos mock en services
crear feature de reservas
conectar frontend con backend
Objetivo de esta base

Este esqueleto actual busca:

tener una base visual y estructural limpia
facilitar el trabajo en equipo
permitir crecer sin rehacer la arquitectura
preparar el proyecto para futuras integraciones con backend
Notas importantes para el equipo
mantener la estructura por features
no mezclar lógica de datos con layout
reutilizar componentes siempre que sea posible
dejar las páginas como pantallas y mover la lógica reutilizable a components, services o hooks
mantener consistencia en nombres de archivos y componentes
Estado actual resumido

Actualmente ya está construido:

login funcional mock
rutas protegidas
layout privado
dashboard básico
página de inmuebles
formulario mock de creación de inmuebles

La prioridad ahora es consolidar esta base y seguir ampliando funcionalidad.
