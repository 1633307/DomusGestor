import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../app/authContext";
import { usersApi } from "../../services/api";
import styles from "./GestioPage.module.css";

const emptyForm = {
  username: "",
  first_name: "",
  last_name: "",
  email: "",
  nip: "",
  is_admin: false,
  password: "",
};

export default function GestioPage() {
  const { user: currentUser, isAdmin } = useAuth();
  const navigate = useNavigate();

  const [users, setUsers]                         = useState([]);
  const [loading, setLoading]                     = useState(true);
  const [error, setError]                         = useState("");
  const [modalDeshabilitar, setModalDeshabilitar] = useState(null);
  const [modalHabilitar, setModalHabilitar]       = useState(null);
  const [modalEliminar, setModalEliminar]         = useState(null);
  const [modalForm, setModalForm]                 = useState(null); // null | "create" | user object
  const [form, setForm]                           = useState(emptyForm);
  const [formError, setFormError]                 = useState("");
  const [saving, setSaving]                       = useState(false);

  useEffect(() => {
    if (!isAdmin) {
      navigate("/dashboard");
      return;
    }
    loadUsers();
  }, [isAdmin]);

  const loadUsers = () => {
    setLoading(true);
    usersApi
      .list()
      .then((data) => setUsers(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  const handleDeshabilitar = async () => {
    try {
      await usersApi.patch(modalDeshabilitar.id, { is_active: false });
      setUsers((prev) =>
        prev.map((u) =>
          u.id === modalDeshabilitar.id ? { ...u, is_active: false } : u
        )
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setModalDeshabilitar(null);
    }
  };

  const handleHabilitar = async () => {
    try {
      await usersApi.patch(modalHabilitar.id, { is_active: true });
      setUsers((prev) =>
        prev.map((u) =>
          u.id === modalHabilitar.id ? { ...u, is_active: true } : u
        )
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setModalHabilitar(null);
    }
  };

  const handleEliminar = async () => {
    try {
      await usersApi.remove(modalEliminar.id);
      setUsers((prev) => prev.filter((u) => u.id !== modalEliminar.id));
    } catch (err) {
      setError(err.message);
    } finally {
      setModalEliminar(null);
    }
  };

  const openCreate = () => {
    setForm(emptyForm);
    setFormError("");
    setModalForm("create");
  };

  const openEdit = (u) => {
    setForm({
      username:   u.username,
      first_name: u.first_name || "",
      last_name:  u.last_name  || "",
      email:      u.email,
      nip:        u.nip,
      is_admin:   u.is_admin,
      password:   "",
    });
    setFormError("");
    setModalForm(u);
  };

  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
  };

  const handleFormSubmit = async () => {
    setSaving(true);
    setFormError("");
    try {
      if (modalForm === "create") {
        const created = await usersApi.create(form);
        setUsers((prev) => [created, ...prev]);
      } else {
        const { password, ...updateData } = form;
        const updated = await usersApi.update(modalForm.id, updateData);
        setUsers((prev) =>
          prev.map((u) => (u.id === modalForm.id ? updated : u))
        );
      }
      setModalForm(null);
    } catch (err) {
      if (err.fieldErrors) {
        const [field, msgs] = Object.entries(err.fieldErrors)[0];
        setFormError(`${field}: ${Array.isArray(msgs) ? msgs[0] : msgs}`);
      } else {
        setFormError(err.message);
      }
    } finally {
      setSaving(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "-";
    return new Date(dateStr).toLocaleDateString("ca-ES", {
      year: "numeric", month: "2-digit", day: "2-digit",
    });
  };

  if (loading) return <p>Carregant usuaris...</p>;

  return (
    <section className={styles.page}>
      <div className={styles.pageHeader}>
        <h2>Gestió d'usuaris</h2>
        <button className={styles.btnNou} onClick={openCreate}>
          Nou usuari
        </button>
      </div>

      {error && <p className={styles.error}>{error}</p>}

      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>NIP</th>
              <th>Nom d'usuari</th>
              <th>Email</th>
              <th>Admin</th>
              <th>Estat</th>
              <th>Data alta</th>
              <th>Accions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => {
              const isSelf = u.id === currentUser?.id;
              return (
                <tr key={u.id} className={!u.is_active ? styles.rowDisabled : ""}>
                  <td>{u.nip}</td>
                  <td>{u.username}</td>
                  <td>{u.email}</td>
                  <td>{u.is_admin ? "Sí" : "No"}</td>
                  <td>
                    {isSelf ? (
                      <span className={styles.badgeSelf}>Tu</span>
                    ) : u.is_active ? (
                      <span className={styles.badgeActiu}>Actiu</span>
                    ) : (
                      <span className={styles.badgeInactiu}>Inactiu</span>
                    )}
                  </td>
                  <td>{formatDate(u.date_joined)}</td>
                  <td className={styles.actions}>
                    {!isSelf && (
                      <>
                        <button
                          className={styles.btnEditar}
                          onClick={() => openEdit(u)}
                        >
                          Editar
                        </button>
                        {u.is_active ? (
                          <button
                            className={styles.btnDeshabilitar}
                            onClick={() => setModalDeshabilitar(u)}
                          >
                            Deshabilitar
                          </button>
                        ) : (
                          <>
                            <button
                              className={styles.btnHabilitar}
                              onClick={() => setModalHabilitar(u)}
                            >
                              Habilitar
                            </button>
                            <button
                              className={styles.btnEliminar}
                              onClick={() => setModalEliminar(u)}
                            >
                              Eliminar
                            </button>
                          </>
                        )}
                      </>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {modalDeshabilitar && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h3>Deshabilitar usuari</h3>
            <p>
              Estàs segur que vols deshabilitar{" "}
              <strong>{modalDeshabilitar.username}</strong>? L'usuari deixarà
              d'estar actiu.
            </p>
            <div className={styles.modalActions}>
              <button
                className={styles.btnCancel}
                onClick={() => setModalDeshabilitar(null)}
              >
                Cancel·lar
              </button>
              <button
                className={styles.btnConfirmDeshabilitar}
                onClick={handleDeshabilitar}
              >
                Deshabilitar
              </button>
            </div>
          </div>
        </div>
      )}

      {modalHabilitar && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h3>Habilitar usuari</h3>
            <p>
              Estàs segur que vols habilitar{" "}
              <strong>{modalHabilitar.username}</strong>? L'usuari tornarà a
              estar actiu.
            </p>
            <div className={styles.modalActions}>
              <button
                className={styles.btnCancel}
                onClick={() => setModalHabilitar(null)}
              >
                Cancel·lar
              </button>
              <button
                className={styles.btnConfirmHabilitar}
                onClick={handleHabilitar}
              >
                Habilitar
              </button>
            </div>
          </div>
        </div>
      )}

      {modalEliminar && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h3>Eliminar usuari</h3>
            <p>
              Estàs segur que vols eliminar{" "}
              <strong>{modalEliminar.username}</strong>? Aquesta acció és
              irreversible i s'eliminaran totes les dades associades.
            </p>
            <div className={styles.modalActions}>
              <button
                className={styles.btnCancel}
                onClick={() => setModalEliminar(null)}
              >
                Cancel·lar
              </button>
              <button
                className={styles.btnConfirmEliminar}
                onClick={handleEliminar}
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}

      {modalForm && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h3>{modalForm === "create" ? "Nou usuari" : "Editar usuari"}</h3>
            {formError && <p className={styles.formError}>{formError}</p>}
            <div className={styles.formGrid}>
              <label>
                NIP
                <input
                  name="nip"
                  value={form.nip}
                  onChange={handleFormChange}
                  autoComplete="off"
                />
              </label>
              <label>
                Nom d'usuari
                <input
                  name="username"
                  value={form.username}
                  onChange={handleFormChange}
                  autoComplete="off"
                />
              </label>
              <label>
                Nom
                <input
                  name="first_name"
                  value={form.first_name}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                Cognom
                <input
                  name="last_name"
                  value={form.last_name}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                Email
                <input
                  name="email"
                  type="email"
                  value={form.email}
                  onChange={handleFormChange}
                  autoComplete="off"
                />
              </label>
              {modalForm === "create" && (
                <label>
                  Contrasenya
                  <input
                    name="password"
                    type="password"
                    value={form.password}
                    onChange={handleFormChange}
                    autoComplete="new-password"
                  />
                </label>
              )}
              <label className={styles.checkboxLabel}>
                <input
                  name="is_admin"
                  type="checkbox"
                  checked={form.is_admin}
                  onChange={handleFormChange}
                />
                Administrador
              </label>
            </div>
            <div className={styles.modalActions}>
              <button
                className={styles.btnCancel}
                onClick={() => setModalForm(null)}
              >
                Cancel·lar
              </button>
              <button
                className={styles.btnConfirmHabilitar}
                onClick={handleFormSubmit}
                disabled={saving}
              >
                {saving ? "Guardant..." : "Guardar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
