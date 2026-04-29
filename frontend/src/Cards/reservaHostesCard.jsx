import styles from "./reservaHostesCard.module.css";

function GuestField({
  label,
  name,
  value,
  onChange,
  isEditing,
  type = "text",
  options = null,
}) {
  return (
    <div className={styles.field}>
      <label>{label}</label>

      {isEditing ? (
        options ? (
          <select name={name} value={value} onChange={onChange}>
            <option value="">Selecciona una opció</option>
            {options.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        ) : (
          <input name={name} type={type} value={value} onChange={onChange} />
        )
      ) : (
        <div className={styles.fieldValue}>{value || "-"}</div>
      )}
    </div>
  );
}

export default function ReservaHostesCard({
  data,
  isEditing,
  onGuestCountChange,
  onGuestChange,
  pendingGuestRemoval,
  onSelectGuestToRemove,
  onConfirmGuestRemoval,
  onCancelGuestRemoval,
}) {
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

  return (
    <div className={styles.wrapper}>
      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <div>
            <h2>Hostes de la reserva</h2>
            <p>Dades personals dels hostes vinculats a la reserva</p>
          </div>
        </div>

        <div className={styles.guestCountBox}>
          <div className={styles.field}>
            <label>Número d&apos;hostes</label>

            {isEditing ? (
              <input
                type="number"
                min="1"
                value={data.guestCount}
                onChange={(e) => onGuestCountChange(Number(e.target.value))}
              />
            ) : (
              <div className={styles.fieldValue}>{data.guestCount || "-"}</div>
            )}
          </div>
        </div>

        {isEditing && pendingGuestRemoval?.isPending && (
          <div className={styles.warningBox}>
            <div>
              <strong>Has reduït el número d&apos;hostes.</strong>
              <p>
                Selecciona quin hoste vols eliminar abans d&apos;aplicar el canvi.
              </p>
            </div>

            <div className={styles.removalActions}>
              <select
                value={pendingGuestRemoval.selectedGuestId || ""}
                onChange={(e) => onSelectGuestToRemove(Number(e.target.value))}
              >
                <option value="">Selecciona un hoste</option>
                {data.guests.map((guest, index) => (
                  <option key={guest.id} value={guest.id}>
                    {guest.isMainGuest
                      ? `Hoste principal - ${guest.fullName || "Sense nom"}`
                      : `Hoste ${index + 1} - ${guest.fullName || "Sense nom"}`}
                  </option>
                ))}
              </select>

              <button
                type="button"
                className={styles.deleteButton}
                onClick={onConfirmGuestRemoval}
                disabled={!pendingGuestRemoval.selectedGuestId}
              >
                Eliminar hoste
              </button>

              <button
                type="button"
                className={styles.cancelButton}
                onClick={onCancelGuestRemoval}
              >
                Cancel·lar
              </button>
            </div>
          </div>
        )}

        <div className={styles.guestsList}>
          {data.guests.map((guest, index) => (
            <section key={guest.id} className={styles.guestCard}>
              <div className={styles.guestHeader}>
                <h3>
                  {guest.isMainGuest
                    ? `Hoste principal - ${guest.fullName || "Sense nom"}`
                    : `Hoste ${index + 1} - ${guest.fullName || "Sense nom"}`}
                </h3>
              </div>

              <div className={styles.formGrid}>
                <GuestField
                  label={guest.isMainGuest ? "Nom hoste principal" : "Nom hoste"}
                  name="fullName"
                  value={guest.fullName}
                  onChange={(e) => onGuestChange(guest.id, e)}
                  isEditing={isEditing}
                />

                <GuestField
                  label={guest.isMainGuest ? "Sexe hoste principal" : "Sexe hoste"}
                  name="gender"
                  value={guest.gender}
                  onChange={(e) => onGuestChange(guest.id, e)}
                  isEditing={isEditing}
                  options={genderOptions}
                />

                {!guest.isMainGuest && (
                  <GuestField
                    label="Relació parental"
                    name="relationship"
                    value={guest.relationship || ""}
                    onChange={(e) => onGuestChange(guest.id, e)}
                    isEditing={isEditing}
                    options={relationshipOptions}
                  />
                )}

                <GuestField
                  label={
                    guest.isMainGuest
                      ? "Tipus de document hoste principal"
                      : "Tipus de document hoste"
                  }
                  name="documentType"
                  value={guest.documentType}
                  onChange={(e) => onGuestChange(guest.id, e)}
                  isEditing={isEditing}
                  options={documentOptions}
                />

                <GuestField
                  label={
                    guest.isMainGuest
                      ? "Número document hoste principal"
                      : "Número document hoste"
                  }
                  name="documentNumber"
                  value={guest.documentNumber}
                  onChange={(e) => onGuestChange(guest.id, e)}
                  isEditing={isEditing}
                />

                <GuestField
                  label={
                    guest.isMainGuest
                      ? "Nacionalitat hoste principal"
                      : "Nacionalitat hoste"
                  }
                  name="nationality"
                  value={guest.nationality}
                  onChange={(e) => onGuestChange(guest.id, e)}
                  isEditing={isEditing}
                />

                <GuestField
                  label={
                    guest.isMainGuest
                      ? "Data de naixement hoste principal"
                      : "Data de naixement hoste"
                  }
                  name="birthDate"
                  value={guest.birthDate}
                  onChange={(e) => onGuestChange(guest.id, e)}
                  isEditing={isEditing}
                  type="date"
                />

                <div className={`${styles.field} ${styles.fullWidth}`}>
                  <label>
                    {guest.isMainGuest
                      ? "Lloc de residència hoste principal"
                      : "Lloc de residència hoste"}
                  </label>

                  {isEditing ? (
                    <input
                      name="residence"
                      value={guest.residence}
                      onChange={(e) => onGuestChange(guest.id, e)}
                      placeholder="Adreça completa, localitat i país"
                    />
                  ) : (
                    <div className={styles.fieldValue}>{guest.residence || "-"}</div>
                  )}
                </div>

                <GuestField
                  label={
                    guest.isMainGuest ? "Correu hoste principal" : "Correu hoste"
                  }
                  name="email"
                  value={guest.email}
                  onChange={(e) => onGuestChange(guest.id, e)}
                  isEditing={isEditing}
                  type="email"
                />

                <GuestField
                  label={
                    guest.isMainGuest ? "Telèfon hoste principal" : "Telèfon hoste"
                  }
                  name="phone"
                  value={guest.phone}
                  onChange={(e) => onGuestChange(guest.id, e)}
                  isEditing={isEditing}
                />
              </div>
            </section>
          ))}
        </div>
      </section>
    </div>
  );
}