import { useState } from 'react';
import Sidebar from '../layout/Sidebar';
import FooterActions from '../layout/FooterActions';
import style from './InfoInmoblePage.module.css';
import PerfilCard from '../../Cards/perfilCard';

const initialData = {
  propertyName: "Apartament Sitges Centre",
  reference: "DG-001",
  address: "Carrer Sant Pau, 12, 2n 1a",
  city: "Sitges",
  postalCode: "08870",
  propertyType: "Pis",
  capacity: "4",
  bedrooms: "2",
  bathrooms: "1",
  basePrice: "120",
  mainPhoto: "/placeHolderCasa.jpg",

  ownerName: "Joan Serra Pujol",
  ownerTaxId: "12345678A",
  ownerEmail: "joan.serra@gmail.com",
  ownerPhone: "+34 600 123 456",
  ownerAddress: "Carrer Major, 25, Barcelona",
  ownerIban: "ES21 2100 0418 4502 0005 1332",
};

export default function InfoInmoble() {
  const [seccioActiva, setSeccioActiva] = useState('perfil');
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState(initialData);
  const [draftData, setDraftData] = useState(initialData);

  const handleEdit = () => {
    setDraftData(formData);
    setIsEditing(true);
  };

  const handleCancel = () => {
    setDraftData(formData);
    setIsEditing(false);
  };

  const handleSave = () => {
    setFormData(draftData);
    setIsEditing(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    setDraftData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <section>
      <div className={style.templateGrid}>
        <Sidebar
          setSeccioActiva={setSeccioActiva}
          seccioActiva={seccioActiva}
        />

        <div className={style.perfilCard}>
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
            />
          )}
        </div>
      </div>
    </section>
  );
}