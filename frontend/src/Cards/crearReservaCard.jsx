import { useMemo, useState } from "react";
import styles from "./crearReservaCard.module.css";

function createEmptyHoste(index = 0) {
  return {
    id: `hoste-${Date.now()}-${index}`,
    isMainGuest: index === 0,
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
  };
}

const emptyForm = {
  dataEntrada: "",
  dataSortida: "",
  numHostes: "1",
  tipusReserva: "Airbnb",
  estatReserva: "prereservada",
  net: "false",
  comentarisInterns: "",
  descompteIndividualAplicat: "false",
  descompteIndividualPercentatge: "",
  descompteIndividualMotiu: "",
  hostes: [createEmptyHoste(0)],
};

const genderOptions = ["Home", "Dona", "Altres"];
const documentOptions = ["DNI", "NIE", "Passaport"];
const relationshipOptions = [
  "Fill/a",
  "Parella",
  "Pare/Mare",
  "Germà/Germana",
  "Avi/Àvia",
  "Net/a",
  "Altres",
];

function toBoolean(value) {
  return value === true || value === "true" || value === "Sí" || value === "Si";
}

function formatBoolean(value) {
  return toBoolean(value) ? "Sí" : "No";
}

function formatPercentatge(value, isActive) {
  if (!isActive) return "-";
  return value ? `${value}%` : "-";
}

function Field({
  label,
  name,
  value,
  onChange,
  type = "text",
  options,
  textarea = false,
  readOnly = false,
  fullWidth = false,
  min,
  max,
}) {
  return (
    <div className={`${styles.field} ${fullWidth ? styles.fullWidth : ""}`}>
      <label>{label}</label>

      {readOnly ? (
        <div className={styles.fieldValue}>{value || "-"}</div>
      ) : options ? (
        <select name={name} value={value} onChange={onChange}>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ) : textarea ? (
        <textarea name={name} value={value} onChange={onChange} rows="5" />
      ) : (
        <input
          name={name}
          type={type}
          value={value}
          onChange={onChange}
          min={min}
          max={max}
        />
      )}
    </div>
  );
}

function GuestField({
  label,
  name,
  value,
  onChange,
  type = "text",
  options,
  fullWidth = false,
  placeholder,
}) {
  return (
    <div className={`${styles.field} ${fullWidth ? styles.fullWidth : ""}`}>
      <label>{label}</label>

      {options ? (
        <select name={name} value={value} onChange={onChange}>
          <option value="">Selecciona una opció</option>
          {options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      ) : (
        <input
          name={name}
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
        />
      )}
    </div>
  );
}

function hosteFrontToBackend(guest, index) {
  return {
    es_principal: index === 0,
    nom_complet: guest.fullName ?? "",
    genere: guest.gender ?? "",
    relacio_parental: index === 0 ? "" : guest.relationship ?? "",
    tipus_document: guest.documentType ?? "",
    numero_document: guest.documentNumber ?? "",
    nacionalitat: guest.nationality ?? "",
    data_naixement: guest.birthDate || null,
    residencia: guest.residence ?? "",
    email: guest.email ?? "",
    telefon: guest.phone ?? "",
  };
}

export default function CrearReservaCard({ immoble, onPreview, onCreate, isCreating = false, initialDataEntrada = "", initialDataSortida = "" }) {
  const [form, setForm] = useState({ ...emptyForm, dataEntrada: initialDataEntrada, dataSortida: initialDataSortida });
  const [errors, setErrors] = useState([]);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [previewError, setPreviewError] = useState("");
  const [previewReserva, setPreviewReserva] = useState(null);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [pendingForm, setPendingForm] = useState(null);

  const descompteImmobleActiu = toBoolean(immoble?.descompteActiu);
  const descompteImmoblePercentatge = immoble?.descomptePercentatge || "";

  const immobleNom = useMemo(
    () => immoble?.propertyName || immoble?.nom_comercial || "-",
    [immoble]
  );

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === "numHostes") {
      const nextCount = Math.max(Number(value) || 1, 1);
      setForm((prev) => {
        const nextHostes = [...prev.hostes];

        if (nextCount > nextHostes.length) {
          for (let index = nextHostes.length; index < nextCount; index += 1) {
            nextHostes.push(createEmptyHoste(index));
          }
        }

        return {
          ...prev,
          numHostes: String(nextCount),
          hostes: nextHostes.slice(0, nextCount).map((hoste, index) => ({
            ...hoste,
            isMainGuest: index === 0,
          })),
        };
      });
      return;
    }

    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleHosteChange = (guestId, e) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      hostes: prev.hostes.map((hoste) =>
        hoste.id === guestId ? { ...hoste, [name]: value } : hoste
      ),
    }));
  };

  const validate = () => {
    const nextErrors = [];
    const hostes = form.hostes;
    const individualPercentatge = Number(form.descompteIndividualPercentatge) || 0;
    const immoblePercentatge = Number(descompteImmoblePercentatge) || 0;

    if (!form.dataEntrada) nextErrors.push("La data d'entrada és obligatòria.");
    if (!form.dataSortida) nextErrors.push("La data de sortida és obligatòria.");
    if (form.dataEntrada && form.dataSortida && form.dataSortida <= form.dataEntrada) {
      nextErrors.push("La data de sortida ha de ser posterior a la data d'entrada.");
    }
    if (!hostes.length) {
      nextErrors.push("Cal introduir almenys un hoste.");
    }

    const mainGuest = hostes[0];
    if (!mainGuest?.fullName.trim()) {
      nextErrors.push("El nom complet de l'hoste principal és obligatori.");
    }
    if (!mainGuest?.documentType) {
      nextErrors.push("El tipus de document de l'hoste principal és obligatori.");
    }
    if (!mainGuest?.documentNumber.trim()) {
      nextErrors.push("El número de document de l'hoste principal és obligatori.");
    }

    hostes.slice(1).forEach((hoste, index) => {
      if (!hoste.fullName.trim()) {
        nextErrors.push(`El nom complet de l'hoste ${index + 2} és obligatori.`);
      }
    });

    if (Number(form.numHostes) !== hostes.length) {
      nextErrors.push("El nombre d'hostes no coincideix amb els formularis d'hoste.");
    }
    if (immoblePercentatge < 0 || immoblePercentatge > 100) {
      nextErrors.push("El percentatge de descompte de l'immoble ha d'estar entre 0 i 100.");
    }
    if (individualPercentatge < 0 || individualPercentatge > 100) {
      nextErrors.push("El percentatge de descompte individual ha d'estar entre 0 i 100.");
    }

    setErrors(nextErrors);
    return nextErrors.length === 0;
  };

  const buildSubmissionData = () => ({
    ...form,
    hostes: form.hostes.map(hosteFrontToBackend),
    numHostes: String(form.hostes.length),
    descompteImmobleAplicat: descompteImmobleActiu,
    descompteImmoblePercentatge,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    const submissionData = buildSubmissionData();
    setIsPreviewing(true);
    setPreviewError("");
    setPreviewReserva(null);

    try {
      if (!onPreview) {
        await onCreate(submissionData);
        return;
      }
      const preview = await onPreview(submissionData);
      setPendingForm(submissionData);
      setPreviewReserva(preview);
      setIsPreviewOpen(true);
    } catch {
      setPreviewError("No s'ha pogut calcular el resum econòmic de la reserva.");
    } finally {
      setIsPreviewing(false);
    }
  };

  const handleConfirmReserva = async () => {
    if (!pendingForm) return;
    setIsPreviewOpen(false);
    await onCreate(pendingForm);
  };

  const handleClosePreview = () => {
    setIsPreviewOpen(false);
  };

  return (
    <div className={styles.wrapper}>
      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h2>Nova reserva</h2>
            <p>Crear una reserva associada a aquest immoble</p>
          </div>
        </div>

        {errors.length > 0 && (
          <div className={styles.errorBox}>
            {errors.map((error) => (
              <p key={error}>{error}</p>
            ))}
          </div>
        )}

        {previewError && (
          <div className={styles.errorBox}>
            <p>{previewError}</p>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className={styles.formGrid}>
            <Field label="Immoble reservat" value={immobleNom} readOnly />
            <Field
              label="Data d'entrada"
              name="dataEntrada"
              value={form.dataEntrada}
              onChange={handleChange}
              type="date"
            />
            <Field
              label="Data de sortida"
              name="dataSortida"
              value={form.dataSortida}
              onChange={handleChange}
              type="date"
            />
            <Field
              label="Nombre d'hostes"
              name="numHostes"
              value={form.numHostes}
              onChange={handleChange}
              type="number"
              min="1"
            />
            <Field
              label="Tipus de reserva"
              name="tipusReserva"
              value={form.tipusReserva}
              onChange={handleChange}
              options={[
                { value: "Airbnb", label: "Airbnb" },
                { value: "Booking", label: "Booking" },
                { value: "Direct", label: "Directa" },
                { value: "Altres", label: "Altres" },
              ]}
            />
            <Field
              label="Estat de la reserva"
              name="estatReserva"
              value={form.estatReserva}
              onChange={handleChange}
              options={[
                { value: "prereservada", label: "Prereservada" },
                { value: "reservada", label: "Reservada" },
                { value: "lista", label: "Llesta" },
                { value: "cancelada", label: "Cancel·lada" },
              ]}
            />
            <Field
              label="Net"
              name="net"
              value={form.net}
              onChange={handleChange}
              options={[
                { value: "true", label: "Sí" },
                { value: "false", label: "No" },
              ]}
            />
            <Field
              label="Comentaris interns"
              name="comentarisInterns"
              value={form.comentarisInterns}
              onChange={handleChange}
              textarea
              fullWidth
            />
          </div>

          <div className={styles.sectionBlock}>
            <h3>Descomptes aplicats</h3>
            <div className={styles.formGrid}>
              <Field
                label="Descompte de l'immoble aplicat"
                value={formatBoolean(descompteImmobleActiu)}
                readOnly
              />
              <Field
                label="Percentatge descompte immoble"
                value={formatPercentatge(
                  descompteImmoblePercentatge,
                  descompteImmobleActiu
                )}
                readOnly
              />
              <Field
                label="Descompte individual aplicat"
                name="descompteIndividualAplicat"
                value={form.descompteIndividualAplicat}
                onChange={handleChange}
                options={[
                  { value: "true", label: "Sí" },
                  { value: "false", label: "No" },
                ]}
              />
              <Field
                label="Percentatge descompte individual"
                name="descompteIndividualPercentatge"
                value={form.descompteIndividualPercentatge}
                onChange={handleChange}
                type="number"
                min="0"
                max="100"
              />
              <Field
                label="Motiu del descompte"
                name="descompteIndividualMotiu"
                value={form.descompteIndividualMotiu}
                onChange={handleChange}
                textarea
                fullWidth
              />
            </div>
          </div>

          <div className={styles.sectionBlock}>
            <h3>Hostes de la reserva</h3>
            <div className={styles.guestsList}>
              {form.hostes.map((hoste, index) => (
                <section className={styles.guestCard} key={hoste.id}>
                  <div className={styles.guestHeader}>
                    <h4>{index === 0 ? "Hoste principal" : `Hoste ${index + 1}`}</h4>
                  </div>

                  <div className={styles.formGrid}>
                    <GuestField
                      label="Nom complet"
                      name="fullName"
                      value={hoste.fullName}
                      onChange={(e) => handleHosteChange(hoste.id, e)}
                    />
                    <GuestField
                      label="Sexe"
                      name="gender"
                      value={hoste.gender}
                      onChange={(e) => handleHosteChange(hoste.id, e)}
                      options={genderOptions}
                    />
                    {index > 0 && (
                      <GuestField
                        label="Relació parental"
                        name="relationship"
                        value={hoste.relationship}
                        onChange={(e) => handleHosteChange(hoste.id, e)}
                        options={relationshipOptions}
                      />
                    )}
                    <GuestField
                      label="Tipus de document"
                      name="documentType"
                      value={hoste.documentType}
                      onChange={(e) => handleHosteChange(hoste.id, e)}
                      options={documentOptions}
                    />
                    <GuestField
                      label="Número document"
                      name="documentNumber"
                      value={hoste.documentNumber}
                      onChange={(e) => handleHosteChange(hoste.id, e)}
                    />
                    <GuestField
                      label="Nacionalitat"
                      name="nationality"
                      value={hoste.nationality}
                      onChange={(e) => handleHosteChange(hoste.id, e)}
                    />
                    <GuestField
                      label="Data de naixement"
                      name="birthDate"
                      value={hoste.birthDate}
                      onChange={(e) => handleHosteChange(hoste.id, e)}
                      type="date"
                    />
                    <GuestField
                      label="Lloc de residència"
                      name="residence"
                      value={hoste.residence}
                      onChange={(e) => handleHosteChange(hoste.id, e)}
                      placeholder="Adreça completa, localitat i país"
                      fullWidth
                    />
                    <GuestField
                      label="Correu"
                      name="email"
                      value={hoste.email}
                      onChange={(e) => handleHosteChange(hoste.id, e)}
                      type="email"
                    />
                    <GuestField
                      label="Telèfon"
                      name="phone"
                      value={hoste.phone}
                      onChange={(e) => handleHosteChange(hoste.id, e)}
                    />
                  </div>
                </section>
              ))}
            </div>
          </div>

          <div className={styles.actions}>
            <button type="submit" disabled={isCreating || isPreviewing}>
              {isPreviewing ? "Calculant..." : isCreating ? "Creant..." : "Reservar"}
            </button>
          </div>
        </form>
      </section>

      {isPreviewOpen && previewReserva && (
        <div className={styles.previewOverlay} role="presentation">
          <section
            className={styles.previewModal}
            role="dialog"
            aria-modal="true"
            aria-labelledby="resum-reserva-title"
          >
            <div className={styles.previewHeader}>
              <div>
                <h2 id="resum-reserva-title">Resum de la reserva</h2>
                <p>
                  {previewReserva.nits} nits · {previewReserva.num_hostes} hostes
                </p>
              </div>
            </div>

            <div className={styles.previewRows}>
              <div className={styles.previewRow}>
                <span>Preu de l'allotjament</span>
                <strong>{previewReserva.subtotal_allotjament} €</strong>
              </div>
              {Number(previewReserva.descompte_immoble_import) > 0 && (
                <div className={styles.previewRow}>
                  <span>
                    Descompte de l'immoble ({previewReserva.descompte_immoble_percentatge}%)
                  </span>
                  <strong>-{previewReserva.descompte_immoble_import} €</strong>
                </div>
              )}
              {Number(previewReserva.descompte_individual_import) > 0 && (
                <div className={styles.previewRow}>
                  <span>
                    Descompte individual ({previewReserva.descompte_individual_percentatge}%)
                  </span>
                  <strong>-{previewReserva.descompte_individual_import} €</strong>
                </div>
              )}
              <div className={`${styles.previewRow} ${styles.previewSubtotal}`}>
                <span>Total allotjament</span>
                <strong>{previewReserva.total_allotjament} €</strong>
              </div>
              <div className={styles.previewRow}>
                <span>
                  Comissió de la immobiliària ({previewReserva.comissio_percentatge_mitjana}%)
                </span>
                <strong>{previewReserva.comissio_import} €</strong>
              </div>
              <div className={styles.previewRow}>
                <span>
                  Taxa turística ({previewReserva.taxa_turistica_per_hoste_nit} €/hoste/nit)
                </span>
                <strong>{previewReserva.taxa_turistica_import} €</strong>
              </div>
              <div className={`${styles.previewRow} ${styles.previewTotal}`}>
                <span>Total a abonar pel turista</span>
                <strong>{previewReserva.total_a_abonar_turista} €</strong>
              </div>
            </div>

            {previewReserva.linies_nits?.length > 0 && (
              <div className={styles.previewNights}>
                <h3>Detall per nit</h3>
                <div className={styles.previewNightsList}>
                  {previewReserva.linies_nits.map((linia) => (
                    <div className={styles.previewNightRow} key={linia.data}>
                      <span>
                        {linia.data}
                        {linia.temporada ? ` · ${linia.temporada}` : ""}
                      </span>
                      <strong>{linia.preu_nit} €</strong>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className={styles.previewActions}>
              <button
                type="button"
                className={styles.secondaryButton}
                onClick={handleClosePreview}
                disabled={isCreating}
              >
                Tornar a editar
              </button>
              <button
                type="button"
                className={styles.confirmButton}
                onClick={handleConfirmReserva}
                disabled={isCreating}
              >
                {isCreating ? "Creant..." : "Confirmar reserva"}
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
