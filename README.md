# Domus Gestor - Laboratori Integrat de Software 2026

Sistema integral per a la gestió d'allotjaments turístics centralitzant reserves, immobles i clients.

## 🚀 Stack Tecnològic
- **Frontend:** React
- **Backend:** Django API REST
- **Base de dades:** PostgreSQL
- **Infraestructura:** Oracle Cloud

## 👥 Equip
- **Frontend:** Adam Jiménez, Marc Morató, Peixian Wang.
- **Backend:** Pol Pedro, Sergi Muñoz, Arnau Trucharte.

## 📅 Planificació
Treballem amb metodologia **Scrum** en sprints de 3 setmanes.

🏗️ Arquitectura del Projecte (MVC Desacoblat)

El projecte segueix un patró **Model-Vista-Controlador** on el Backend (Django) actua com a Model i Controlador, i el Frontend (React) actua com a Vista.

```text
domus-gestor/
├── backend/               # MODEL & CONTROLADOR (Django + PostgreSQL)
│   ├── core/              # Configuració global del projecte
│   ├── users/             # Gestió d'Usuaris, Staff, Propietaris i Inquilins
│   ├── properties/        # Gestió d'Immobles, Inventari i Temporades 
│   └── bookings/          # Motor de reserves, Pagaments i Registre Mossos 
├── frontend/              # VISTA (React.js)
│   ├── public/            # Actius estàtics
│   └── src/
│       ├── components/    # UI reusable (Calendari, Forms, Taules)
│       └── pages/         # Vistes de l'aplicació (Dashboard, Portal Client) 
├── docs/                  # Documentació (Contracte, Diagrames ER) 
├── .gitignore             # Fitxers exclosos (node_modules, .env, __pycache__)
└── README.md              # Documentació principal
