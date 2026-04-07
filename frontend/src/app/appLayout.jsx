import { Outlet } from 'react-router-dom';
import Header from '../components/layout/header';
import Sidebar from '../components/layout/sidebar';

export default function AppLayout() {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <Header />
        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}