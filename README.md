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

domus-gestor/
├── backend/               # El "Model" i "Controlador" (Django)
│   ├── core/              # Configuració del projecte
│   ├── users/             # App per a Usuaris, Propietaris i Inquilins
│   ├── properties/        # App per a Immobles i Temporades
│   └── bookings/          # App per a Reserves i Pagaments
├── frontend/              # La "Vista" (React)
│   ├── src/
│   │   ├── components/    # Calendari, Formularis, etc.
│   │   └── pages/         # Dashboard, Login, Detall Immoble
├── docs/                  # Documentació (Contrato.pdf, Diagrames) 
├── .gitignore             # Per no pujar brossa al repo
└── README.md              # Descripció i guia del projecte
