import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import Sidebar from '../layout/Sidebar';
import FooterActions from '../layout/FooterActions';
import style from './InfoInmoblePage.module.css';
import PerfilCard from '../../Cards/perfilCard';
import { propertiesApi } from '../../services/api';

const emptyForm = {
  propertyName: '',
  reference: '',
  address: '',
  city: '',
  postalCode: '',
  propertyType: '',
  capacity: '',
  bedrooms: '',
  bathrooms: '',
  basePrice: '',
  mainPhoto: '',
  ownerName: '',
  ownerTaxId: '',
  ownerEmail: '',
  ownerPhone: '',
  ownerAddress: '',
  ownerIban: '',
};

function backendToForm(p) {
  return {
    propertyName: p.nom_comercial ?? '',
    reference: p.referencia ?? '',
    address: p.adreca ?? '',
    city: p.ciutat ?? '',
    postalCode: p.codi_postal ?? '',
    propertyType: p.tipus_immoble ?? '',
    capacity: String(p.capacitat_maxima ?? ''),
    bedrooms: String(p.num_habitacions ?? ''),
    bathrooms: String(p.num_banys ?? ''),
    basePrice: String(p.preu_base_nit ?? ''),
    mainPhoto: p.foto_principal ?? '',
    ownerName: p.propietari_nom ?? '',
    ownerTaxId: p.propietari_dni ?? '',
    ownerEmail: p.propietari_email ?? '',
    ownerPhone: p.propietari_telefon ?? '',
    ownerAddress: p.propietari_adreca ?? '',
    ownerIban: p.propietari_iban ?? '',
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
    foto_principal: f.mainPhoto,
    propietari_nom: f.ownerName,
    propietari_dni: f.ownerTaxId,
    propietari_email: f.ownerEmail,
    propietari_telefon: f.ownerPhone,
    propietari_adreca: f.ownerAddress,
    propietari_iban: f.ownerIban,
    metres_quadrats: original?.metres_quadrats ?? 0,
    descripcio: original?.descripcio ?? '',
    actiu: original?.actiu ?? true,
  };
}

export default function InfoInmoble() {
  const { id } = useParams();
  const [seccioActiva, setSeccioActiva] = useState('perfil');
  const [isEditing, setIsEditing] = useState(false);
  const [original, setOriginal] = useState(null);
  const [formData, setFormData] = useState(emptyForm);
  const [draftData, setDraftData] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

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
    setError('');
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

  if (loading) return <p>Carregant immoble...</p>;

  return (
    <section>
      <div className={style.templateGrid}>
        <Sidebar setSeccioActiva={setSeccioActiva} seccioActiva={seccioActiva} />

        <div className={style.perfilCard}>
          {error && <p style={{ color: 'red' }}>{error}</p>}

          {seccioActiva === 'perfil' && (
            <>
              <h2>Perfil de l'immoble</h2>
              <PerfilCard
                data={isEditing ? draftData : formData}
                isEditing={isEditing}
                onChange={handleChange}
              />
            </>
          )}

          {seccioActiva === 'fotos' && (<div><h2>Galeria de Fotos</h2></div>)}
          {seccioActiva === 'incidencies' && (<div><h2>Gestió d'Incidències</h2></div>)}

          {seccioActiva === 'perfil' && (
            <FooterActions
              isEditing={isEditing}
              onEdit={handleEdit}
              onCancel={handleCancel}
              onSave={handleSave}
              isSaveDisabled={saving}
              saveLabel={saving ? 'Guardant...' : 'Guardar'}
            />
          )}
        </div>
      </div>
    </section>
  );
}
