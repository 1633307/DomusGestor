import { useEffect, useState } from "react";
import FooterActions from "../layout/FooterActions";
import ImmobiliariaInfoSection from "./profile/ImmobiliariaInfoSection";
import { immobiliariaApi } from "../../services/api";
import styles from "./PerfilImmobiliariaPage.module.css";

const STORAGE_KEY = "domus_immobiliaria_profile";

const emptyProfile = {
  id: null,
  nomComercial: "",
  raoSocial: "",
  nifCif: "",
  telefon: "",
  correuElectronic: "",
  adreca: "",
  codiPostal: "",
  ciutat: "",
  provincia: "",
  pais: "",
  web: "",
  observacionsInternes: "",
};

function loadLocalProfile() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? { ...emptyProfile, ...JSON.parse(stored) } : emptyProfile;
  } catch {
    return emptyProfile;
  }
}

function saveLocalProfile(profile) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
}

function backendToForm(data, localProfile) {
  if (!data) return localProfile;

  return {
    ...emptyProfile,
    ...localProfile,
    id: data.id ?? localProfile.id,
    nomComercial: data.nom_comercial ?? localProfile.nomComercial,
    nifCif: data.cif ?? localProfile.nifCif,
    telefon: data.telefon ?? localProfile.telefon,
    correuElectronic: data.email_contacte ?? localProfile.correuElectronic,
    adreca: data.adreca ?? localProfile.adreca,
  };
}

function formToBackend(profile) {
  return {
    nom_comercial: profile.nomComercial,
    cif: profile.nifCif,
    adreca: profile.adreca,
    email_contacte: profile.correuElectronic,
    telefon: profile.telefon,
  };
}

export default function PerfilImmobiliariaPage() {
  const [isEditing, setIsEditing] = useState(false);
  const [profile, setProfile] = useState(emptyProfile);
  const [draftProfile, setDraftProfile] = useState(emptyProfile);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    const localProfile = loadLocalProfile();

    immobiliariaApi
      .list()
      .then((items) => {
        const backendProfile = Array.isArray(items) ? items[0] : items;
        const mapped = backendToForm(backendProfile, localProfile);
        setProfile(mapped);
        setDraftProfile(mapped);
      })
      .catch(() => {
        setProfile(localProfile);
        setDraftProfile(localProfile);
        setNotice("S'estan mostrant les dades guardades localment.");
      })
      .finally(() => setLoading(false));
  }, []);

  const handleEdit = () => {
    setDraftProfile(profile);
    setIsEditing(true);
    setError("");
    setNotice("");
  };

  const handleCancel = () => {
    setDraftProfile(profile);
    setIsEditing(false);
    setError("");
  };

  const handleSave = async () => {
    setSaving(true);
    setError("");
    setNotice("");

    try {
      let savedProfile = draftProfile;

      // TODO: ampliar el model/API d'InfoImmobiliaria amb raó social, codi
      // postal, ciutat, província, país, web i observacions internes. Fins
      // aleshores aquests camps es conserven a localStorage.
      try {
        const payload = formToBackend(draftProfile);
        const backendSaved = draftProfile.id
          ? await immobiliariaApi.update(draftProfile.id, payload)
          : await immobiliariaApi.create(payload);

        savedProfile = backendToForm(backendSaved, draftProfile);
      } catch {
        setNotice("Dades guardades localment. Restarà pendent sincronitzar-les amb el backend.");
      }

      saveLocalProfile(savedProfile);
      setProfile(savedProfile);
      setDraftProfile(savedProfile);
      setIsEditing(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setDraftProfile((prev) => ({ ...prev, [name]: value }));
  };

  if (loading) return <p>Carregant perfil de la immobiliària...</p>;

  const currentProfile = isEditing ? draftProfile : profile;
  const profileName = currentProfile.nomComercial || "Immobiliària";
  const profileMeta =
    currentProfile.correuElectronic || currentProfile.nifCif || "Dades pendents";
  const initials = profileName
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word.charAt(0))
    .join("")
    .toUpperCase();

  return (
    <section className={styles.page}>
      <div className={styles.pageHeader}>
        <h1>Perfil de la immobiliària</h1>
        <p>Gestiona la informació general i de contacte de la immobiliària</p>
      </div>

      {error && <p className={styles.error}>{error}</p>}
      {notice && <p className={styles.notice}>{notice}</p>}

      <div className={styles.profileSummary}>
        <div className={styles.profileAvatar}>{initials || "IM"}</div>
        <div>
          <h2>{profileName}</h2>
          <p>{profileMeta}</p>
        </div>
      </div>

      <ImmobiliariaInfoSection
        data={currentProfile}
        isEditing={isEditing}
        onChange={handleChange}
      />

      <FooterActions
        isEditing={isEditing}
        onEdit={handleEdit}
        onCancel={handleCancel}
        onSave={handleSave}
        isSaveDisabled={saving}
        cancelLabel="Cancel·lar"
        saveLabel={saving ? "Guardant..." : "Guardar"}
      />
    </section>
  );
}
