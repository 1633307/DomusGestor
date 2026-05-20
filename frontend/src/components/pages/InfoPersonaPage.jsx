import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import FooterActions from "../layout/FooterActions";
import { inquilinsApi } from "../../services/api";
import PersonaFormSection from "./persones/PersonaFormSection";
import styles from "./InfoPersonaPage.module.css";

const emptyPersona = {
  id: null,
  fullName: "",
  gender: "",
  documentType: "",
  documentNumber: "",
  nationality: "",
  birthDate: "",
  residence: "",
  email: "",
  phone: "",
  fiscalName: "",
  fiscalId: "",
  billingAddress: "",
  billingPostalCode: "",
  billingCity: "",
  billingProvince: "",
  billingCountry: "",
  billingEmail: "",
  billingPhone: "",
  billingNotes: "",
};

function backendToForm(persona) {
  if (!persona) return emptyPersona;

  return {
    id: persona.id ?? null,
    fullName: persona.nom_complet ?? persona.fullName ?? "",
    gender: persona.genere ?? "",
    documentType: persona.tipus_document ?? "",
    documentNumber: persona.dni_passaport ?? persona.documentNumber ?? "",
    nationality: persona.nacionalitat ?? persona.nationality ?? "",
    birthDate: persona.data_naixement ?? "",
    residence: persona.residencia ?? "",
    email: persona.email ?? "",
    phone: persona.telefon ?? persona.phone ?? "",
    fiscalName: persona.nom_fiscal ?? "",
    fiscalId: persona.nif_cif ?? "",
    billingAddress: persona.adreca_facturacio ?? "",
    billingPostalCode: persona.codi_postal_facturacio ?? "",
    billingCity: persona.ciutat_facturacio ?? "",
    billingProvince: persona.provincia_facturacio ?? "",
    billingCountry: persona.pais_facturacio ?? "",
    billingEmail: persona.email_facturacio ?? "",
    billingPhone: persona.telefon_facturacio ?? "",
    billingNotes:
      persona.observacions_facturacio || persona.dades_facturacio || "",
  };
}

function formToBackend(form) {
  return {
    nom_complet: form.fullName.trim(),
    genere: form.gender,
    tipus_document: form.documentType,
    dni_passaport: form.documentNumber.trim(),
    nacionalitat: form.nationality,
    data_naixement: form.birthDate || null,
    residencia: form.residence,
    email: form.email,
    telefon: form.phone,
    nom_fiscal: form.fiscalName,
    nif_cif: form.fiscalId,
    adreca_facturacio: form.billingAddress,
    codi_postal_facturacio: form.billingPostalCode,
    ciutat_facturacio: form.billingCity,
    provincia_facturacio: form.billingProvince,
    pais_facturacio: form.billingCountry,
    email_facturacio: form.billingEmail,
    telefon_facturacio: form.billingPhone,
    observacions_facturacio: form.billingNotes,
    dades_facturacio: form.billingNotes,
  };
}

function validatePersona(form) {
  const errors = [];
  if (!form.fullName.trim()) errors.push("El nom complet és obligatori.");
  if (form.documentNumber.trim() && !form.documentType) {
    errors.push("El tipus de document és obligatori si introdueixes el número de document.");
  }
  if (form.documentType && !form.documentNumber.trim()) {
    errors.push("El número de document és obligatori si introdueixes el tipus de document.");
  }
  return errors;
}

export default function InfoPersonaPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isNew = !id;
  const [isEditing, setIsEditing] = useState(isNew);
  const [persona, setPersona] = useState(emptyPersona);
  const [draftPersona, setDraftPersona] = useState(emptyPersona);
  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isNew) {
      setPersona(emptyPersona);
      setDraftPersona(emptyPersona);
      setIsEditing(true);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError("");
    inquilinsApi
      .get(id)
      .then((data) => {
        const mapped = backendToForm(data);
        setPersona(mapped);
        setDraftPersona(mapped);
      })
      .catch(() => setError("No s'han pogut carregar les dades de la persona."))
      .finally(() => setLoading(false));
  }, [id, isNew]);

  const currentPersona = isEditing ? draftPersona : persona;
  const title = useMemo(() => {
    if (isNew) return "Nova persona";
    return currentPersona.fullName || "Persona";
  }, [currentPersona.fullName, isNew]);

  const handleEdit = () => {
    setDraftPersona(persona);
    setIsEditing(true);
    setError("");
  };

  const handleCancel = () => {
    if (isNew) {
      navigate("/persones");
      return;
    }
    setDraftPersona(persona);
    setIsEditing(false);
    setError("");
  };

  const handleSave = async () => {
    const validationErrors = validatePersona(draftPersona);
    if (validationErrors.length) {
      setError(validationErrors[0]);
      return;
    }

    setSaving(true);
    setError("");
    try {
      const payload = formToBackend(draftPersona);
      const saved = isNew
        ? await inquilinsApi.create(payload)
        : await inquilinsApi.update(id, payload);
      const mapped = backendToForm(saved);
      setPersona(mapped);
      setDraftPersona(mapped);
      setIsEditing(false);

      if (isNew) {
        if (saved?.id) navigate(`/persones/${saved.id}`);
        else navigate("/persones");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setDraftPersona((prev) => ({ ...prev, [name]: value }));
  };

  if (loading) return <p>Carregant persona...</p>;

  return (
    <section>
      <div className={styles.page}>
        <div className={styles.pageHeader}>
          <div>
            <h2>{title}</h2>
            <p>Gestió de dades personals, contacte i facturació</p>
          </div>
          <button
            type="button"
            className={styles.secondaryButton}
            onClick={() => navigate("/persones")}
          >
            Tornar
          </button>
        </div>

        {error && <p className={styles.error}>{error}</p>}

        <PersonaFormSection
          data={currentPersona}
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
      </div>
    </section>
  );
}
