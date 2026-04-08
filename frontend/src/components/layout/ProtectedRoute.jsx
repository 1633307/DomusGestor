import { Navigate } from 'react-router-dom';
import { useAuth } from '../../features/auth/authContext';

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) return <p>Cargando...</p>;

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
