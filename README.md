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
[cite_start]│   ├── properties/        # Gestió d'Immobles, Inventari i Temporades [cite: 49]
[cite_start]│   └── bookings/          # Motor de reserves, Pagaments i Registre Mossos [cite: 50, 51]
├── frontend/              # VISTA (React.js)
│   ├── public/            # Actius estàtics
│   └── src/
[cite_start]│       ├── components/    # UI reusable (Calendari, Forms, Taules) [cite: 80]
[cite_start]│       └── pages/         # Vistes de l'aplicació (Dashboard, Portal Client) [cite: 153]
[cite_start]├── docs/                  # Documentació (Contracte, Diagrames ER) [cite: 1]
├── .gitignore             # Fitxers exclosos (node_modules, .env, __pycache__)
└── README.md              # Documentació principal
