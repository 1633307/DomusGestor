import { Outlet } from 'react-router-dom';
import Header from '../components/layout/Header';
import Sidebar from '../components/layout/Sidebar';
import styles from './appLayout.module.css';

export default function AppLayoutSideBar() {
  return (
    <div className={styles.appMain}>
      <Header />
      <div className={styles.appShell}>
        <Sidebar />
        <main className={styles.pageContent}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}