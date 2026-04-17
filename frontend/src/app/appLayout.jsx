import { Outlet } from 'react-router-dom';
import Header from '../components/layout/Header';
import Sidebar from '../components/layout/Sidebar';
import styles from './appLayout.module.css';

export default function AppLayout() {
  return (
    <div className={styles.appShell}>
      <Sidebar />
      <div className={styles.appMain}>
        <Header />
        <main className={styles.pageContent}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}