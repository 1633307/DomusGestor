import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Sidebar from "../layout/Sidebar";
import FooterActions from "../layout/FooterActions";
import style from "./InfoInmoblePage.module.css";
import PerfilCard from "../../Cards/perfilCard";
import ImmobleDescompteCard from "../../Cards/immobleDescompteCard";
import CrearReservaCard from "../../Cards/crearReservaCard";
import FotosCard from "../../Cards/fotosCard";
import { bookingsApi, inquilinsApi, propertiesApi } from "../../services/api";

const emptyForm = {
  propertyName: "",
  reference: "",
  address: "",
  city: "",
  postalCode: "",
  propertyType: "",
  capacity: "",
  bedrooms: "",
  bathrooms: "",
  basePrice: "",
  ownerName: "",
  ownerTaxId: "",
  ownerEmail: "",
  ownerPhone: "",
  ownerAddress: "",
  ownerIban: "",
  descompteActiu: false,
  descomptePercentatge: "",
};

function toBoolean(value) {
  return value === true || value === "true" || value === "Sí" || value === "Si";
}

function backendToForm(p) {
  return {
    propertyName: p.nom_comercial ?? "",
    reference: p.referencia ?? "",
    address: p.adreca ?? "",
    city: p.ciutat ?? "",
    postalCode: p.codi_postal ?? "",
    propertyType: p.tipus_immoble ?? "",
    capacity: String(p.capacitat_maxima ?? ""),
    bedrooms: String(p.num_habitacions ?? ""),
    bathrooms: String(p.num_banys ?? ""),
    basePrice: String(p.preu_base_nit ?? ""),
    ownerName: p.propietari_nom ?? "",
    ownerTaxId: p.propietari_dni ?? "",
    ownerEmail: p.propietari_email ?? "",
    ownerPhone: p.propietari_telefon ?? "",
    ownerAddress: p.propietari_adreca ?? "",
    ownerIban: p.propietari_iban ?? "",
    descompteActiu: p.descompte_actiu ?? false,
    descomptePercentatge: String(p.descompte_percentatge ?? ""),
  };
}

function formToBackend(f, original) {
  return {
    nom_comercial: f.propertyName,
    referencia: f.reference,
    adreca: f.address,
    ciutat: f.city,
    codi_postal: f.postalCode,
    tipus_immoble: f.propertyType,
    capacitat_maxima: Number(f.capacity) || 0,
    num_habitacions: Number(f.bedrooms) || 0,
    num_banys: Number(f.bathrooms) || 0,
    preu_base_nit: Number(f.basePrice) || 0,
    propietari_nom: f.ownerName,
    propietari_dni: f.ownerTaxId,
    propietari_email: f.ownerEmail,
    propietari_telefon: f.ownerPhone,
    propietari_adreca: f.ownerAddress,
    propietari_iban: f.ownerIban,
    descompte_actiu: toBoolean(f.descompteActiu),
    descompte_percentatge: Number(f.descomptePercentatge) || 0,
    metres_quadrats: original?.metres_quadrats ?? 0,
    descripcio: original?.descripcio ?? "",
    actiu: original?.actiu ?? true,
  };
}

export default function InfoInmoble() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [seccioActiva, setSeccioActiva] = useState("perfil");
  const [isEditing, setIsEditing] = useState(false);
  const [original, setOriginal] = useState(null);
  const [formData, setFormData] = useState(emptyForm);
  const [draftData, setDraftData] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [creatingReserva, setCreatingReserva] = useState(false);

  useEffect(() => {
    if (!id) {
      setLoading(false);
      return;
    }
    setLoading(true);
    propertiesApi
      .get(id)
      .then((data) => {
        setOriginal(data);
        const mapped = backendToForm(data);
        setFormData(mapped);
        setDraftData(mapped);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  const handleEdit = () => {
    setDraftData(formData);
    setIsEditing(true);
  };

  const handleCancel = () => {
    setDraftData(formData);
    setIsEditing(false);
  };

  const handleSave = async () => {
    setSaving(true);
    setError("");
    try {
      const payload = formToBackend(draftData, original);
      const updated = await propertiesApi.update(id, payload);
      setOriginal(updated);
      const mapped = backendToForm(updated);
      setFormData(mapped);
      setDraftData(mapped);
      setIsEditing(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setDraftData((prev) => ({ ...prev, [name]: value }));
  };

  const handleCreateReserva = async (form) => {
    setCreatingReserva(true);
    setError("");
    try {
      const mainGuest = form.hostes[0];
      const inquili = await inquilinsApi.create({
        nom_complet: mainGuest.nom_complet || "Client sense nom",
        dni_passaport: mainGuest.numero_document || `PENDENT-${Date.now()}`,
        email: mainGuest.email || "pendent@example.com",
        dades_facturacio: "",
      });

      const payload = {
        immoble: Number(id),
        inquili: inquili.id,
        data_entrada: form.dataEntrada,
        data_sortida: form.dataSortida,
        num_hostes: form.hostes.length,
        tipus_reserva: form.tipusReserva,
        estat_reserva: form.estatReserva,
        net: toBoolean(form.net),
        comentaris_interns: form.comentarisInterns,
        descompte_immoble_aplicat: toBoolean(form.descompteImmobleAplicat),
        descompte_immoble_percentatge:
          Number(form.descompteImmoblePercentatge) || 0,
        descompte_individual_aplicat: toBoolean(
          form.descompteIndividualAplicat,
        ),
        descompte_individual_percentatge:
          Number(form.descompteIndividualPercentatge) || 0,
        descompte_individual_motiu: form.descompteIndividualMotiu,
        hostes: form.hostes,
      };

      const created = await bookingsApi.create(payload);
      if (created?.id) {
        navigate(`/infoReserva/${created.id}`);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setCreatingReserva(false);
    }
  };

  if (loading) return <p>Carregant immoble...</p>;

  return (
    <section>
      <div className={style.templateGrid}>
        <Sidebar
          setSeccioActiva={setSeccioActiva}
          seccioActiva={seccioActiva}
          seccions={[
            { id: "perfil", label: "Perfil" },
            { id: "descompte", label: "Descompte" },
            { id: "novaReserva", label: "Nova reserva" },
            { id: "fotos", label: "Fotos" },
            { id: "incidencies", label: "Incidéncies" },
          ]}
        />

        <div className={style.perfilCard}>
          {error && <p style={{ color: "red" }}>{error}</p>}

          {seccioActiva === "perfil" && (
            <>
              <h2>Perfil de l'immoble</h2>
              <PerfilCard
                data={isEditing ? draftData : formData}
                isEditing={isEditing}
                onChange={handleChange}
              />
            </>
          )}

          {seccioActiva === "fotos" && (
            <FotosCard fotos={original?.fotos ?? []} />
          )}
          {seccioActiva === "incidencies" && (
            <div>
              <h2>Gestió d'Incidències</h2>
            </div>
          )}
          {seccioActiva === "descompte" && (
            <ImmobleDescompteCard
              data={isEditing ? draftData : formData}
              isEditing={isEditing}
              onChange={handleChange}
            />
          )}
          {seccioActiva === "novaReserva" && (
            <CrearReservaCard
              immoble={{ id, ...formData }}
              onCreate={handleCreateReserva}
              isCreating={creatingReserva}
            />
          )}

          {(seccioActiva === "perfil" || seccioActiva === "descompte") && (
            <FooterActions
              isEditing={isEditing}
              onEdit={handleEdit}
              onCancel={handleCancel}
              onSave={handleSave}
              isSaveDisabled={saving}
              saveLabel={saving ? "Guardant..." : "Guardar"}
            />
          )}
        </div>
      </div>
    </section>
  );
}
