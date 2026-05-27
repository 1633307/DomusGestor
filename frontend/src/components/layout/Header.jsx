import { useEffect, useState } from "react";
import { useAuth } from "../../app/authContext";
import { Link, NavLink } from "react-router-dom";
import { immobiliariaApi } from "../../services/api";
import styles from "./Header.module.css";

const STORAGE_KEY = "domus_immobiliaria_profile";
const PROFILE_UPDATED_EVENT = "domus_immobiliaria_profile_updated";

const emptyProfile = {
  nomComercial: "",
  logoBase64: "",
};

function loadLocalProfile() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? { ...emptyProfile, ...JSON.parse(stored) } : emptyProfile;
  } catch {
    return emptyProfile;
  }
}

function backendToHeaderProfile(data, localProfile) {
  if (!data) return localProfile;
  return {
    ...localProfile,
    nomComercial: data.nom_comercial ?? localProfile.nomComercial,
  };
}

export default function Header() {
  const { user, logout, isAdmin } = useAuth();
  const [profile, setProfile] = useState(() => loadLocalProfile());
  const displayName = profile.nomComercial || "Immobiliària";
  const initial = displayName.charAt(0).toUpperCase() || "I";

  useEffect(() => {
    const localProfile = loadLocalProfile();
    setProfile(localProfile);

    immobiliariaApi
      .list()
      .then((items) => {
        const backendProfile = Array.isArray(items) ? items[0] : items;
        setProfile(backendToHeaderProfile(backendProfile, loadLocalProfile()));
      })
      .catch(() => {
        setProfile(loadLocalProfile());
      });

    const handleProfileUpdated = (event) => {
      setProfile(event.detail ?? loadLocalProfile());
    };

    const handleStorage = (event) => {
      if (event.key === STORAGE_KEY) {
        setProfile(loadLocalProfile());
      }
    };

    window.addEventListener(PROFILE_UPDATED_EVENT, handleProfileUpdated);
    window.addEventListener("storage", handleStorage);

    return () => {
      window.removeEventListener(PROFILE_UPDATED_EVENT, handleProfileUpdated);
      window.removeEventListener("storage", handleStorage);
    };
  }, []);

  return (
    <header className={styles.header}>
      <div className={styles.col1}>
        <h1 className={styles.title}>Domus Gestor</h1>
      </div>

      <div className={styles.headerActions}>
        <Link
          to="/perfil-immobiliaria"
          className={styles.userLink}
          title="Perfil de la immobiliària"
        >
          <span className={styles.avatar}>
            {profile.logoBase64 ? (
              <img src={profile.logoBase64} alt="Logo de la immobiliària" />
            ) : (
              initial
            )}
          </span>
          <span>{displayName}</span>
        </Link>
        <span>{user?.username || "Usuari"}</span>
        <button className={styles.secondaryButton} onClick={logout}>
          Tancar sessió
        </button>
      </div>

      <div className={styles.fila}>
        <nav className={styles.sidebarNav}>
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              isActive ? `${styles.link} ${styles.activeLink}` : styles.link
            }
          >
            Dashboard
          </NavLink>

          <NavLink
            to="/inmobles"
            className={({ isActive }) =>
              isActive ? `${styles.link} ${styles.activeLink}` : styles.link
            }
          >
            Immobles
          </NavLink>

          <NavLink
            to="/reserves"
            className={({ isActive }) =>
              isActive ? `${styles.link} ${styles.activeLink}` : styles.link
            }
          >
            Reserves
          </NavLink>

          <NavLink
            to="/persones"
            className={({ isActive }) =>
              isActive ? `${styles.link} ${styles.activeLink}` : styles.link
            }
          >
            Persones
          </NavLink>

          <NavLink
            to="/calendari"
            className={({ isActive }) =>
              isActive ? `${styles.link} ${styles.activeLink}` : styles.link
            }
          >
            Calendari
          </NavLink>

          {isAdmin && (
            <NavLink
              to="/gestio"
              className={({ isActive }) =>
                isActive ? `${styles.link} ${styles.activeLink}` : styles.link
              }
            >
              Gestió
            </NavLink>
          )}
        </nav>
      </div>
    </header>
  );
}
