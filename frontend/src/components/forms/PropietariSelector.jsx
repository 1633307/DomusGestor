import { useState } from "react";
import { personesApi, perfilsPropietariApi } from "../../services/api";
import styles from "./PropietariSelector.module.css";

function mapPersonaToPropietariData(persona) {
  const p = persona.perfil_propietari;
  return {
    ownerName: persona.nom_complet ?? "",
    ownerEmail: persona.email ?? "",
    ownerPhone: persona.telefon ?? "",
    ownerTaxId: p?.nif_cif ?? "",
    ownerAddress: p?.adreca_facturacio ?? "",
    ownerIban: p?.iban ?? "",
  };
}

const emptyPerfilForm = {
  nom_fiscal: "",
  nif_cif: "",
  adreca_facturacio: "",
  iban: "",
};

const emptyNovaPersonaForm = {
  nom_complet: "",
  dni_passaport: "",
  email: "",
  telefon: "",
  nom_fiscal: "",
  nif_cif: "",
  adreca_facturacio: "",
  iban: "",
};

export default function PropietariSelector({ propietariId, propietariData, isEditing, onChange }) {
  const [modalOpen, setModalOpen] = useState(false);
  const [persones, setPersones] = useState([]);
  const [search, setSearch] = useState("");
  const [step, setStep] = useState("list");
  const [selectedPersona, setSelectedPersona] = useState(null);
  const [perfilForm, setPerfilForm] = useState(emptyPerfilForm);
  const [novaPersonaForm, setNovaPersonaForm] = useState(emptyNovaPersonaForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const openModal = () => {
    setModalOpen(true);
    setStep("list");
    setSearch("");
    setError("");
    personesApi
      .list()
      .then((data) => setPersones(data.results ?? data))
      .catch(() => setError("No s'han pogut carregar les persones."));
  };

  const closeModal = () => {
    setModalOpen(false);
    setSelectedPersona(null);
    setPerfilForm(emptyPerfilForm);
    setNovaPersonaForm(emptyNovaPersonaForm);
    setSaving(false);
    setError("");
  };

  const filtered = persones.filter(
    (p) =>
      !search ||
      p.nom_complet?.toLowerCase().includes(search.toLowerCase()) ||
      p.email?.toLowerCase().includes(search.toLowerCase()) ||
      p.dni_passaport?.toLowerCase().includes(search.toLowerCase()),
  );

  const propietaris = filtered.filter((p) => p.perfil_propietari !== null);
  const altres = filtered.filter((p) => p.perfil_propietari === null);

  const handleSelectPropietari = (persona) => {
    onChange(persona.id, mapPersonaToPropietariData(persona));
    closeModal();
  };

  const handleSelectAltra = (persona) => {
    setSelectedPersona(persona);
    setPerfilForm({
      nom_fiscal: persona.nom_complet ?? "",
      nif_cif: persona.dni_passaport ?? "",
      adreca_facturacio: "",
      iban: "",
    });
    setStep("addPerfil");
  };

  const handleAddPerfil = async () => {
    setSaving(true);
    setError("");
    try {
      await perfilsPropietariApi.create({
        persona: selectedPersona.id,
        nom_fiscal: perfilForm.nom_fiscal,
        nif_cif: perfilForm.nif_cif,
        adreca_facturacio: perfilForm.adreca_facturacio,
        iban: perfilForm.iban,
      });
      const updated = await personesApi.get(selectedPersona.id);
      onChange(selectedPersona.id, mapPersonaToPropietariData(updated));
      closeModal();
    } catch (err) {
      setError(err.message);
      setSaving(false);
    }
  };

  const handleNovaPersona = async () => {
    if (!novaPersonaForm.nom_complet.trim()) {
      setError("El nom complet és obligatori.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const persona = await personesApi.create({
        nom_complet: novaPersonaForm.nom_complet,
        dni_passaport: novaPersonaForm.dni_passaport,
        email: novaPersonaForm.email,
        telefon: novaPersonaForm.telefon,
      });
      await perfilsPropietariApi.create({
        persona: persona.id,
        nom_fiscal: novaPersonaForm.nom_fiscal || novaPersonaForm.nom_complet,
        nif_cif: novaPersonaForm.nif_cif || novaPersonaForm.dni_passaport,
        adreca_facturacio: novaPersonaForm.adreca_facturacio,
        iban: novaPersonaForm.iban,
      });
      const updated = await personesApi.get(persona.id);
      onChange(persona.id, mapPersonaToPropietariData(updated));
      closeModal();
    } catch (err) {
      setError(err.message);
      setSaving(false);
    }
  };

  if (!isEditing) {
    return (
      <div className={styles.readOnly}>
        {propietariData?.ownerName ? (
          <div className={styles.fieldGrid}>
            <div className={styles.field}>
              <span className={styles.fieldLabel}>Nom</span>
              <div className={styles.fieldValue}>{propietariData.ownerName || "-"}</div>
            </div>
            <div className={styles.field}>
              <span className={styles.fieldLabel}>DNI / NIF</span>
              <div className={styles.fieldValue}>{propietariData.ownerTaxId || "-"}</div>
            </div>
            <div className={styles.field}>
              <span className={styles.fieldLabel}>Email</span>
              <div className={styles.fieldValue}>{propietariData.ownerEmail || "-"}</div>
            </div>
            <div className={styles.field}>
              <span className={styles.fieldLabel}>Telèfon</span>
              <div className={styles.fieldValue}>{propietariData.ownerPhone || "-"}</div>
            </div>
            <div className={`${styles.field} ${styles.fullWidth}`}>
              <span className={styles.fieldLabel}>Adreça fiscal</span>
              <div className={styles.fieldValue}>{propietariData.ownerAddress || "-"}</div>
            </div>
            <div className={`${styles.field} ${styles.fullWidth}`}>
              <span className={styles.fieldLabel}>IBAN</span>
              <div className={styles.fieldValue}>{propietariData.ownerIban || "-"}</div>
            </div>
          </div>
        ) : (
          <p className={styles.empty}>Sense propietari assignat</p>
        )}
      </div>
    );
  }

  return (
    <div className={styles.selector}>
      {propietariId ? (
        <div className={styles.currentOwner}>
          <span className={styles.currentOwnerName}>
            {propietariData?.ownerName || "Propietari seleccionat"}
          </span>
          <button type="button" className={styles.changeBtn} onClick={openModal}>
            Canviar
          </button>
        </div>
      ) : (
        <button type="button" className={styles.selectBtn} onClick={openModal}>
          Seleccionar propietari
        </button>
      )}

      {modalOpen && (
        <div className={styles.overlay} onClick={closeModal}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h3 className={styles.modalTitle}>
                {step === "list" && "Seleccionar propietari"}
                {step === "addPerfil" &&
                  `Afegir com a propietari: ${selectedPersona?.nom_complet}`}
                {step === "novaPersona" && "Crear nou propietari"}
              </h3>
              <button type="button" className={styles.closeBtn} onClick={closeModal}>
                ×
              </button>
            </div>

            {error && <p className={styles.error}>{error}</p>}

            {step === "list" && (
              <>
                <input
                  className={styles.searchInput}
                  placeholder="Cercar per nom, email o document..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  autoFocus
                />

                {propietaris.length > 0 && (
                  <>
                    <p className={styles.groupLabel}>Propietaris existents</p>
                    <ul className={styles.list}>
                      {propietaris.map((p) => (
                        <li
                          key={p.id}
                          className={styles.listItem}
                          onClick={() => handleSelectPropietari(p)}
                        >
                          <strong>{p.nom_complet}</strong>
                          <span>{p.email || p.telefon || ""}</span>
                        </li>
                      ))}
                    </ul>
                  </>
                )}

                {altres.length > 0 && (
                  <>
                    <p className={styles.groupLabel}>Altres persones</p>
                    <ul className={styles.list}>
                      {altres.map((p) => (
                        <li
                          key={p.id}
                          className={styles.listItem}
                          onClick={() => handleSelectAltra(p)}
                        >
                          <strong>{p.nom_complet}</strong>
                          <span>{p.email || p.telefon || ""}</span>
                        </li>
                      ))}
                    </ul>
                  </>
                )}

                {filtered.length === 0 && (
                  <p className={styles.empty}>Sense resultats per a "{search}"</p>
                )}

                <div className={styles.modalFooter}>
                  <button
                    type="button"
                    className={styles.newBtn}
                    onClick={() => setStep("novaPersona")}
                  >
                    + Crear persona nova
                  </button>
                </div>
              </>
            )}

            {step === "addPerfil" && (
              <div className={styles.perfilForm}>
                <p className={styles.hint}>
                  Completa les dades fiscals per vincular aquesta persona com a propietari.
                </p>
                <label className={styles.formField}>
                  Nom fiscal
                  <input
                    value={perfilForm.nom_fiscal}
                    onChange={(e) =>
                      setPerfilForm((p) => ({ ...p, nom_fiscal: e.target.value }))
                    }
                  />
                </label>
                <label className={styles.formField}>
                  NIF / CIF
                  <input
                    value={perfilForm.nif_cif}
                    onChange={(e) =>
                      setPerfilForm((p) => ({ ...p, nif_cif: e.target.value }))
                    }
                  />
                </label>
                <label className={styles.formField}>
                  Adreça de facturació
                  <input
                    value={perfilForm.adreca_facturacio}
                    onChange={(e) =>
                      setPerfilForm((p) => ({ ...p, adreca_facturacio: e.target.value }))
                    }
                  />
                </label>
                <label className={styles.formField}>
                  IBAN
                  <input
                    value={perfilForm.iban}
                    onChange={(e) =>
                      setPerfilForm((p) => ({ ...p, iban: e.target.value }))
                    }
                  />
                </label>
                <div className={styles.modalFooter}>
                  <button
                    type="button"
                    className={styles.cancelBtn}
                    onClick={() => setStep("list")}
                  >
                    ← Tornar
                  </button>
                  <button
                    type="button"
                    className={styles.newBtn}
                    onClick={handleAddPerfil}
                    disabled={saving}
                  >
                    {saving ? "Guardant..." : "Afegir com a propietari"}
                  </button>
                </div>
              </div>
            )}

            {step === "novaPersona" && (
              <div className={styles.perfilForm}>
                <p className={styles.hint}>Dades personals</p>
                <label className={styles.formField}>
                  Nom complet <span className={styles.required}>*</span>
                  <input
                    value={novaPersonaForm.nom_complet}
                    onChange={(e) =>
                      setNovaPersonaForm((p) => ({ ...p, nom_complet: e.target.value }))
                    }
                  />
                </label>
                <label className={styles.formField}>
                  DNI / Passaport
                  <input
                    value={novaPersonaForm.dni_passaport}
                    onChange={(e) =>
                      setNovaPersonaForm((p) => ({ ...p, dni_passaport: e.target.value }))
                    }
                  />
                </label>
                <label className={styles.formField}>
                  Email
                  <input
                    type="email"
                    value={novaPersonaForm.email}
                    onChange={(e) =>
                      setNovaPersonaForm((p) => ({ ...p, email: e.target.value }))
                    }
                  />
                </label>
                <label className={styles.formField}>
                  Telèfon
                  <input
                    value={novaPersonaForm.telefon}
                    onChange={(e) =>
                      setNovaPersonaForm((p) => ({ ...p, telefon: e.target.value }))
                    }
                  />
                </label>
                <p className={styles.hint}>Dades fiscals</p>
                <label className={styles.formField}>
                  Nom fiscal
                  <input
                    value={novaPersonaForm.nom_fiscal}
                    onChange={(e) =>
                      setNovaPersonaForm((p) => ({ ...p, nom_fiscal: e.target.value }))
                    }
                  />
                </label>
                <label className={styles.formField}>
                  NIF / CIF
                  <input
                    value={novaPersonaForm.nif_cif}
                    onChange={(e) =>
                      setNovaPersonaForm((p) => ({ ...p, nif_cif: e.target.value }))
                    }
                  />
                </label>
                <label className={styles.formField}>
                  Adreça de facturació
                  <input
                    value={novaPersonaForm.adreca_facturacio}
                    onChange={(e) =>
                      setNovaPersonaForm((p) => ({
                        ...p,
                        adreca_facturacio: e.target.value,
                      }))
                    }
                  />
                </label>
                <label className={styles.formField}>
                  IBAN
                  <input
                    value={novaPersonaForm.iban}
                    onChange={(e) =>
                      setNovaPersonaForm((p) => ({ ...p, iban: e.target.value }))
                    }
                  />
                </label>
                <div className={styles.modalFooter}>
                  <button
                    type="button"
                    className={styles.cancelBtn}
                    onClick={() => setStep("list")}
                  >
                    ← Tornar
                  </button>
                  <button
                    type="button"
                    className={styles.newBtn}
                    onClick={handleNovaPersona}
                    disabled={saving || !novaPersonaForm.nom_complet.trim()}
                  >
                    {saving ? "Creant..." : "Crear i assignar propietari"}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
