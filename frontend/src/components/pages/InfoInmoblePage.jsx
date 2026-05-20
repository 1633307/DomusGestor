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
import TemporadesCard from "../../Cards/temporadesCard";
import ServeisCard from "../../Cards/serveisCard";
import HorarisCard from "../../Cards/horarisCard";
import HistoricPagamentsCard from "../../Cards/historicPagamentsCard";
import ImmobleCalendariCard from "../../Cards/immobleCalendariCard";

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
  temporades: [],
  horaCheckinInici: "",
  horaCheckinFi: "",
  horaCheckoutInici: "",
  horaCheckoutFi: "",
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
    temporades: p.temporades,
    serveis: p.serveis,
    horaCheckinInici: p.hora_checkin_inici ?? "",
    horaCheckinFi: p.hora_checkin_fi ?? "",
    horaCheckoutInici: p.hora_checkout_inici ?? "",
    horaCheckoutFi: p.hora_checkout_fi ?? "",
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
    temporades: f.temporades,
    serveis: f.serveis,
    hora_checkin_inici: f.horaCheckinInici || null,
    hora_checkin_fi: f.horaCheckinFi || null,
    hora_checkout_inici: f.horaCheckoutInici || null,
    hora_checkout_fi: f.horaCheckoutFi || null,
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
  const [hasDraftChanges, setHasDraftChanges] = useState(false);
  const [creatingReserva, setCreatingReserva] = useState(false);
  const [calendarDates, setCalendarDates] = useState({ dataEntrada: "", dataSortida: "" });
  const [actiu, setActiu] = useState(true);

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
        setActiu(data.actiu ?? true);
        const mapped = backendToForm(data);
        setFormData(mapped);
        setDraftData(mapped);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  const handleEdit = () => {
    setDraftData(formData);
    setHasDraftChanges(false);
    setIsEditing(true);
  };

  const handleCancel = () => {
    setDraftData(formData);
    setHasDraftChanges(false);
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
      setHasDraftChanges(false);
      setIsEditing(false);
      return true;
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setHasDraftChanges(true);
    setDraftData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFerReservaFromCalendari = (dataEntrada, dataSortida) => {
    setCalendarDates({ dataEntrada, dataSortida });
    setSeccioActiva("novaReserva");
  };

  const handlePreviewReserva = async (form) => {
    const payload = {
      immoble: Number(id),
      data_entrada: form.dataEntrada,
      data_sortida: form.dataSortida,
      num_hostes: form.hostes.length,
      descompte_immoble_aplicat: toBoolean(form.descompteImmobleAplicat),
      descompte_immoble_percentatge:
        Number(form.descompteImmoblePercentatge) || 0,
      descompte_individual_aplicat: toBoolean(
        form.descompteIndividualAplicat,
      ),
      descompte_individual_percentatge:
        Number(form.descompteIndividualPercentatge) || 0,
    };

    return bookingsApi.preview(payload);
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

  const handleDeshabilitar = async () => {
    setError("");
    try {
      await propertiesApi.patch(id, { actiu: false });
      setActiu(false);
      setOriginal((prev) => ({ ...prev, actiu: false }));
    } catch (err) {
      setError(err.message);
    }
  };

  const handleHabilitar = async () => {
    setError("");
    try {
      await propertiesApi.patch(id, { actiu: true });
      setActiu(true);
      setOriginal((prev) => ({ ...prev, actiu: true }));
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEliminar = async () => {
    setError("");
    try {
      await propertiesApi.remove(id);
      navigate("/inmobles");
    } catch (err) {
      setError(err.message);
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
            { id: "calendari", label: "Calendari" },
            { id: "novaReserva", label: "Nova reserva" },
            { id: "fotos", label: "Fotos" },
            { id: "horaris", label: "Horaris" },
            { id: "temporades", label: "Temporades" },
            { id: "serveis", label: "Serveis" },
            { id: "pagaments", label: "Pagaments" },
            { id: "incidencies", label: "Incidències" },
          ]}
          actiu={actiu}
          onDeshabilitar={handleDeshabilitar}
          onHabilitar={handleHabilitar}
          onEliminar={handleEliminar}
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
          {seccioActiva === "calendari" && (
            <ImmobleCalendariCard
              immobleId={id}
              onFerReserva={handleFerReservaFromCalendari}
            />
          )}
          {seccioActiva === "novaReserva" && (
            <CrearReservaCard
              key={`${calendarDates.dataEntrada}-${calendarDates.dataSortida}`}
              immoble={{ id, ...formData }}
              onPreview={handlePreviewReserva}
              onCreate={handleCreateReserva}
              isCreating={creatingReserva}
              initialDataEntrada={calendarDates.dataEntrada}
              initialDataSortida={calendarDates.dataSortida}
            />
          )}
          {seccioActiva === "horaris" && (
            <HorarisCard
              data={isEditing ? draftData : formData}
              isEditing={isEditing}
              onChange={handleChange}
            />
          )}
          {seccioActiva === "temporades" && (
            <TemporadesCard
              immoble={{ id, ...draftData }}
              setImmoble={setDraftData}
              onSave={handleSave}
            />
          )}
          {seccioActiva === "serveis" && (
            <ServeisCard
              immoble={{ id, ...draftData }}
              setImmoble={setDraftData}
              onSave={handleSave}
            />
          )}
          {seccioActiva === "pagaments" && (
            <HistoricPagamentsCard immobleId={id} />
          )}

          {(seccioActiva === "perfil" || seccioActiva === "descompte" || seccioActiva === "horaris") && (
            <FooterActions
              isEditing={isEditing}
              onEdit={handleEdit}
              onCancel={handleCancel}
              onSave={handleSave}
              isSaveDisabled={saving}
              saveLabel={saving ? "Guardant..." : "Guardar"}
              hasChanges={hasDraftChanges}
            />
          )}
        </div>
      </div>
    </section>
  );
}
