import { Navigate } from "react-router-dom";
import { useAuth } from "./app/authContext";

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (!loading && !isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
