import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Sidebar from "../layout/Sidebar";
import style from "./InfoReservaPage.module.css";
import PageFooterActions from "../layout/FooterActions";
import ReservaInfoCard from "../../Cards/reservaInfoCard";
import ReservaHostesCard from "../../Cards/reservaHostesCard";
import ReservaPagamentsCard from "../../Cards/reservaPagamentsCard";
import ReservaComunicacionsCard from "../../Cards/reservaComunicacionsCard";
import { bookingsApi } from "../../services/api";

// ── Mappers backend <-> frontend ────────────────────────────────────────────
function reservaBackendToInfo(r) {
  return {
    guestCount: String(r.num_hostes ?? r.hostes?.length ?? 0),
    reservationCode: r.codi_reserva ?? "",
    startDate: r.data_entrada ?? "",
    endDate: r.data_sortida ?? "",
    reservedProperty: r.immoble_nom ?? "",
    reservationType: r.tipus_reserva ?? "",
    estadoReserva: r.estat_reserva ?? r.estadoReserva ?? r.estado_reserva ?? "",
    limpio: r.net ?? r.limpio ?? false,
    internalComments: r.comentaris_interns ?? "",
  };
}

function reservaBackendToPagaments(r) {
  return {
    descompteImmobleAplicat: r.descompte_immoble_aplicat ?? false,
    descompteImmoblePercentatge: String(r.descompte_immoble_percentatge ?? ""),
    descompteIndividualAplicat: r.descompte_individual_aplicat ?? false,
    descompteIndividualPercentatge: String(
      r.descompte_individual_percentatge ?? "",
    ),
    descompteIndividualMotiu: r.descompte_individual_motiu ?? "",
  };
}

function toBoolean(value) {
  return value === true || value === "true" || value === "Sí" || value === "Si";
}

function hosteBackendToFront(h) {
  return {
    id: h.id,
    isMainGuest: !!h.es_principal,
    fullName: h.nom_complet ?? "",
    gender: h.genere ?? "",
    relationship: h.relacio_parental ?? "",
    documentType: h.tipus_document ?? "",
    documentNumber: h.numero_document ?? "",
    nationality: h.nacionalitat ?? "",
    birthDate: h.data_naixement ?? "",
    residence: h.residencia ?? "",
    email: h.email ?? "",
    phone: h.telefon ?? "",
  };
}

function hosteFrontToBackend(g) {
  return {
    es_principal: !!g.isMainGuest,
    nom_complet: g.fullName ?? "",
    genere: g.gender ?? "",
    relacio_parental: g.relationship ?? "",
    tipus_document: g.documentType ?? "",
    numero_document: g.documentNumber ?? "",
    nacionalitat: g.nationality ?? "",
    data_naixement: g.birthDate || null,
    residencia: g.residence ?? "",
    email: g.email ?? "",
    telefon: g.phone ?? "",
  };
}

const emptyReserva = {
  guestCount: "0",
  reservationCode: "",
  startDate: "",
  endDate: "",
  reservedProperty: "",
  reservationType: "",
  estadoReserva: "",
  limpio: false,
  internalComments: "",
};

const emptyHostes = { guestCount: 0, guests: [] };

const emptyPagaments = {
  estatPagament: "pendent",
  importTotal: "",
  importPagat: "",
  importPendent: "",
  fianca: "",
  metodePagament: "",
  dataUltimPagament: "",
  observacions: "Encara no hi ha pagaments registrats",
  descompteImmobleAplicat: false,
  descompteImmoblePercentatge: "",
  descompteIndividualAplicat: false,
  descompteIndividualPercentatge: "",
  descompteIndividualMotiu: "",
};

const emptyComunicacio = {
  canal: "Email",
  titol: "",
  destinatari: "",
  data: "",
  estat: "pendent",
  resum: "",
};

const initialComunicacions = [
  {
    id: 1,
    canal: "Email",
    titol: "Confirmació de reserva",
    destinatari: "client@example.com",
    data: "2026-05-02",
    estat: "enviada",
    resum:
      "S'ha enviat la confirmació amb les dates, l'immoble i les dades principals de la reserva.",
  },
  {
    id: 2,
    canal: "WhatsApp",
    titol: "Recordatori de check-in",
    destinatari: "+34 600 000 000",
    data: "2026-05-04",
    estat: "programada",
    resum:
      "Missatge programat amb instruccions d'entrada i informació pràctica per al check-in.",
  },
  {
    id: 3,
    canal: "Sistema",
    titol: "Avís de pagament pendent",
    destinatari: "Equip Domus Gestor",
    data: "2026-05-04",
    estat: "pendent",
    resum:
      "Pendent de confirmar el pagament abans de tancar la reserva com a pagada.",
  },
];

export default function InfoReserva() {
  const { id } = useParams();
  const [seccioActiva, setSeccioActiva] = useState("info");
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState(emptyReserva);
  const [draftData, setDraftData] = useState(emptyReserva);
  const [hostesData, setHostesData] = useState(emptyHostes);
  const [draftHostesData, setDraftHostesData] = useState(emptyHostes);
  const [pagamentsData, setPagamentsData] = useState(emptyPagaments);
  const [draftPagamentsData, setDraftPagamentsData] = useState(emptyPagaments);
  const [comunicacionsData, setComunicacionsData] =
    useState(initialComunicacions);
  const [draftComunicacio, setDraftComunicacio] = useState(emptyComunicacio);

  const [pendingGuestRemoval, setPendingGuestRemoval] = useState({
    isPending: false,
    targetCount: null,
    selectedGuestId: null,
  });

  // ── Carregar dades ─────────────────────────────────────────────────────
  useEffect(() => {
    if (!id) {
      setLoading(false);
      return;
    }
    setLoading(true);
    bookingsApi
      .get(id)
      .then((data) => {
        const info = reservaBackendToInfo(data);
        const pagaments = {
          ...emptyPagaments,
          ...reservaBackendToPagaments(data),
        };
        const guests = (data.hostes || []).map(hosteBackendToFront);
        // Garantim que hi hagi un principal
        if (guests.length && !guests.some((g) => g.isMainGuest)) {
          guests[0].isMainGuest = true;
        }
        const hostes = { guestCount: guests.length, guests };
        setFormData(info);
        setDraftData(info);
        setPagamentsData(pagaments);
        setDraftPagamentsData(pagaments);
        setHostesData(hostes);
        setDraftHostesData(hostes);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  const handleEdit = () => {
    if (seccioActiva === "comunicacions") {
      setDraftComunicacio(emptyComunicacio);
      setIsEditing(true);
      return;
    }

    if (seccioActiva === "pagaments") {
      setDraftPagamentsData(pagamentsData);
      setIsEditing(true);
      return;
    }

    setDraftData(formData);
    setDraftHostesData(hostesData);
    setIsEditing(true);
  };

  const handleCancel = () => {
    if (seccioActiva === "comunicacions") {
      setDraftComunicacio(emptyComunicacio);
      setIsEditing(false);
      return;
    }

    if (seccioActiva === "pagaments") {
      setDraftPagamentsData(pagamentsData);
      setIsEditing(false);
      return;
    }

    setDraftData(formData);
    setDraftHostesData(hostesData);
    setPendingGuestRemoval({
      isPending: false,
      targetCount: null,
      selectedGuestId: null,
    });
    setIsEditing(false);
  };

  const handleSave = async () => {
    if (seccioActiva === "comunicacions") {
      if (!draftComunicacio.titol.trim()) {
        setError("El títol de la comunicació és obligatori.");
        return;
      }

      setComunicacionsData((prev) => [
        {
          ...draftComunicacio,
          id: Date.now(),
          titol: draftComunicacio.titol.trim(),
        },
        ...prev,
      ]);
      setDraftComunicacio(emptyComunicacio);
      setIsEditing(false);
      setError("");
      return;
    }

    if (seccioActiva === "pagaments") {
      setSaving(true);
      setError("");
      try {
        const payload = {
          descompte_immoble_aplicat: toBoolean(
            draftPagamentsData.descompteImmobleAplicat,
          ),
          descompte_immoble_percentatge:
            Number(draftPagamentsData.descompteImmoblePercentatge) || 0,
          descompte_individual_aplicat: toBoolean(
            draftPagamentsData.descompteIndividualAplicat,
          ),
          descompte_individual_percentatge:
            Number(draftPagamentsData.descompteIndividualPercentatge) || 0,
          descompte_individual_motiu:
            draftPagamentsData.descompteIndividualMotiu ?? "",
        };
        const updated = await bookingsApi.update(id, payload);
        const updatedPagaments = {
          ...draftPagamentsData,
          ...reservaBackendToPagaments(updated),
        };
        setPagamentsData(updatedPagaments);
        setDraftPagamentsData(updatedPagaments);
        setIsEditing(false);
      } catch (err) {
        setError(err.message);
      } finally {
        setSaving(false);
      }
      return;
    }

    setSaving(true);
    setError("");
    try {
      // num_hostes sempre derivat de la llista real (no del input pendent)
      const payload = {
        comentaris_interns: draftData.internalComments,
        estat_reserva: draftData.estadoReserva || null,
        net: toBoolean(draftData.limpio),
        descompte_immoble_aplicat: toBoolean(
          pagamentsData.descompteImmobleAplicat,
        ),
        descompte_immoble_percentatge:
          Number(pagamentsData.descompteImmoblePercentatge) || 0,
        descompte_individual_aplicat: toBoolean(
          pagamentsData.descompteIndividualAplicat,
        ),
        descompte_individual_percentatge:
          Number(pagamentsData.descompteIndividualPercentatge) || 0,
        descompte_individual_motiu:
          pagamentsData.descompteIndividualMotiu ?? "",
        num_hostes: draftHostesData.guests.length,
        hostes: draftHostesData.guests.map(hosteFrontToBackend),
      };
      console.log("Payload reserva update:", payload);
      const updated = await bookingsApi.update(id, payload);
      const info = reservaBackendToInfo(updated);
      const pagaments = {
        ...pagamentsData,
        ...reservaBackendToPagaments(updated),
      };
      const guests = (updated.hostes || []).map(hosteBackendToFront);
      if (guests.length && !guests.some((g) => g.isMainGuest)) {
        guests[0].isMainGuest = true;
      }
      const hostes = { guestCount: guests.length, guests };
      setFormData(info);
      setDraftData(info);
      setPagamentsData(pagaments);
      setDraftPagamentsData(pagaments);
      setHostesData(hostes);
      setDraftHostesData(hostes);
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

  const handlePagamentChange = (e) => {
    const { name, value } = e.target;
    setDraftPagamentsData((prev) => ({ ...prev, [name]: value }));
  };

  const handleComunicacioChange = (e) => {
    const { name, value } = e.target;
    setDraftComunicacio((prev) => ({ ...prev, [name]: value }));
  };

  const createEmptyGuest = (id, isMainGuest = false) => ({
    id,
    isMainGuest,
    fullName: "",
    gender: "",
    relationship: "",
    documentType: "",
    documentNumber: "",
    nationality: "",
    birthDate: "",
    residence: "",
    email: "",
    phone: "",
  });

  const handleGuestChange = (guestId, e) => {
    const { name, value } = e.target;
    setDraftHostesData((prev) => ({
      ...prev,
      guests: prev.guests.map((guest) =>
        guest.id === guestId ? { ...guest, [name]: value } : guest,
      ),
    }));
  };

  const handleGuestCountChange = (newCount) => {
    if (!newCount || newCount < 1) return;

    setDraftHostesData((prev) => {
      const currentCount = prev.guests.length;

      if (newCount > currentCount) {
        const guestsToAdd = Array.from(
          { length: newCount - currentCount },
          (_, index) => createEmptyGuest(`new-${Date.now()}-${index}`, false),
        );
        return {
          guestCount: newCount,
          guests: [...prev.guests, ...guestsToAdd],
        };
      }

      if (newCount < currentCount) {
        setPendingGuestRemoval({
          isPending: true,
          targetCount: newCount,
          selectedGuestId: null,
        });
        return { ...prev, guestCount: newCount };
      }

      return { ...prev, guestCount: newCount };
    });
  };

  const handleSelectGuestToRemove = (guestId) => {
    setPendingGuestRemoval((prev) => ({ ...prev, selectedGuestId: guestId }));
  };

  const handleConfirmGuestRemoval = () => {
    const target = pendingGuestRemoval.targetCount;
    let resultLength = 0;

    setDraftHostesData((prev) => {
      const filteredGuests = prev.guests.filter(
        (guest) => guest.id !== pendingGuestRemoval.selectedGuestId,
      );
      const updatedGuests = filteredGuests.map((guest, index) => ({
        ...guest,
        isMainGuest: index === 0,
      }));
      resultLength = updatedGuests.length;
      return {
        guestCount: updatedGuests.length,
        guests: updatedGuests,
      };
    });

    // Si encara hi ha més hostes que el target, segueix demanant més eliminacions
    if (resultLength > target) {
      setPendingGuestRemoval({
        isPending: true,
        targetCount: target,
        selectedGuestId: null,
      });
    } else {
      setPendingGuestRemoval({
        isPending: false,
        targetCount: null,
        selectedGuestId: null,
      });
    }
  };

  const handleCancelGuestRemoval = () => {
    setDraftHostesData((prev) => ({
      ...prev,
      guestCount: prev.guests.length,
    }));
    setPendingGuestRemoval({
      isPending: false,
      targetCount: null,
      selectedGuestId: null,
    });
  };

  if (loading) return <p>Carregant reserva...</p>;

  return (
    <section>
      <div className={style.templateGrid}>
        <Sidebar
          setSeccioActiva={setSeccioActiva}
          seccioActiva={seccioActiva}
          seccions={[
            { id: "info", label: "Informació" },
            { id: "hostes", label: "Hostes" },
            { id: "pagaments", label: "Pagaments" },
            { id: "comunicacions", label: "Comunicacions" },
          ]}
        />
        <div className={style.perfilCard}>
          {error && <p style={{ color: "red" }}>{error}</p>}

          {seccioActiva === "info" && (
            <>
              <h2>
                {formData.reservationCode} - {formData.reservedProperty}
              </h2>
              <ReservaInfoCard
                data={isEditing ? draftData : formData}
                isEditing={isEditing}
                onChange={handleChange}
              />
            </>
          )}
          {seccioActiva === "hostes" && (
            <>
              <h2>Hostes de la reserva</h2>
              <ReservaHostesCard
                data={isEditing ? draftHostesData : hostesData}
                isEditing={isEditing}
                onGuestCountChange={handleGuestCountChange}
                onGuestChange={handleGuestChange}
                pendingGuestRemoval={pendingGuestRemoval}
                onSelectGuestToRemove={handleSelectGuestToRemove}
                onConfirmGuestRemoval={handleConfirmGuestRemoval}
                onCancelGuestRemoval={handleCancelGuestRemoval}
              />
            </>
          )}
          {seccioActiva === "pagaments" && (
            <ReservaPagamentsCard
              data={isEditing ? draftPagamentsData : pagamentsData}
              isEditing={isEditing}
              onChange={handlePagamentChange}
            />
          )}
          {seccioActiva === "comunicacions" && (
            <ReservaComunicacionsCard
              comunicacions={comunicacionsData}
              draftComunicacio={draftComunicacio}
              isEditing={isEditing}
              onDraftChange={handleComunicacioChange}
            />
          )}

          {(seccioActiva === "info" ||
            seccioActiva === "hostes" ||
            seccioActiva === "pagaments" ||
            seccioActiva === "comunicacions") && (
            <PageFooterActions
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
