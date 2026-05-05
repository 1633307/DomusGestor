import styles from "./FooterActions.module.css";

export default function FooterActions({
  isEditing,
  onEdit,
  onCancel,
  onSave,
  editLabel = "Editar",
  cancelLabel = "Cancel·lar",
  saveLabel = "Guardar",
  isSaveDisabled = false,
}) {
  return (
    <div className={styles.footer}>
      <div className={styles.actions}>
        {!isEditing ? (
          <button
            type="button"
            className={styles.editButton}
            onClick={onEdit}
          >
            {editLabel}
          </button>
        ) : (
          <>
            <button
              type="button"
              className={styles.cancelButton}
              onClick={onCancel}
            >
              {cancelLabel}
            </button>

            <button
              type="button"
              className={styles.saveButton}
              onClick={onSave}
              disabled={isSaveDisabled}
            >
              {saveLabel}
            </button>
          </>
        )}
      </div>
    </div>
  );
}