import { Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './appLayout';
import ProtectedRoute from '../ProtectedRoute';
import LoginPage from '../components/pages/LoginPage';
import DashboardPage from '../components/pages/DashboardPage';
import CercadorPage from '../components/pages/CercadorPage';
import InmoblesPage from '../components/pages/InmoblesPage';
import InfoInmoble from '../components/pages/InfoInmoblePage';
import ReservesPage from '../components/pages/reservesPage';
import InfoReserva from '../components/pages/infoReservaPage';
import PerfilImmobiliariaPage from '../components/pages/PerfilImmobiliariaPage';
import PersonesPage from '../components/pages/PersonesPage';
import InfoPersonaPage from '../components/pages/InfoPersonaPage';

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
        <Route path="persones" element={<PersonesPage />} />
        <Route path="persones/nova" element={<InfoPersonaPage />} />
        <Route path="persones/:id" element={<InfoPersonaPage />} />
        <Route path="infoInmoble/:id" element={<InfoInmoble />} />
        <Route path="infoReserva/:id" element={<InfoReserva />} />
        <Route path="perfil-immobiliaria" element={<PerfilImmobiliariaPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
