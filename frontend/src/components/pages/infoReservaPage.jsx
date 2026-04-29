import {useState} from 'react';
import Sidebar from '../layout/Sidebar';
import style from './InfoReservaPage.module.css';
import PageFooterActions from '../layout/FooterActions';
import ReservaInfoCard from '../../Cards/reservaInfoCard';
import ReservaHostesCard from '../../Cards/reservaHostesCard';

const initialReservaData = {
  guestCount: '4',
  reservationCode: 'RES-2026-001',
  startDate: '12-04-2026',
  endDate: '18-04-2026',
  reservedProperty: 'Apartament Sitges Centre',
  reservationType: 'Airbnb',
  internalComments: 'Client sol·licita entrada abans de les 15:00.',
};

const initialHostesData = {
  guestCount: 2,
  guests: [
    {
      id: 1,
      isMainGuest: true,
      fullName: 'Laura Garcia',
      gender: 'Dona',
      relationship: '',
      documentType: 'DNI',
      documentNumber: '12345678A',
      nationality: 'Espanyola',
      birthDate: '1992-05-14',
      residence: 'Carrer Major 12, Barcelona, Espanya',
      email: 'laura.garcia@email.com',
      phone: '+34 600 123 456',
    },
    {
      id: 2,
      isMainGuest: false,
      fullName: 'Marc Garcia',
      gender: 'Home',
      relationship: '',
      documentType: 'DNI',
      documentNumber: '87654321B',
      nationality: 'Espanyola',
      birthDate: '1990-09-02',
      residence: 'Carrer Major 12, Barcelona, Espanya',
      email: 'marc.garcia@email.com',
      phone: '+34 600 654 321',
    },
  ],
};

export default function InfoReserva() {
    const [seccioActiva, setSeccioActiva] = useState('info');
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState(initialReservaData);
    const [draftData, setDraftData] = useState(initialReservaData);
    const [hostesData, setHostesData] = useState(initialHostesData);
    const [draftHostesData, setDraftHostesData] = useState(initialHostesData);

    const [pendingGuestRemoval, setPendingGuestRemoval] = useState({
        isPending: false,
        targetCount: null,
        selectedGuestId: null,
    });

    const handleEdit = () => {
        setDraftData(formData);
        setDraftHostesData(hostesData);
        setIsEditing(true);
    };

    const handleCancel = () => {
        setDraftData(formData);
        setDraftHostesData(hostesData);
        setPendingGuestRemoval({
            isPending: false,
            targetCount: null,
            selectedGuestId: null,
    });
        setIsEditing(false);
    };

    const handleSave = () => {
        setFormData(draftData);
        setHostesData(draftHostesData);
        setIsEditing(false);
    };

    const handleChange = (e) => {
        const { name, value } = e.target;

        setDraftData((prev) => ({
        ...prev,
        [name]: value,
        }));
    };

    const handleSectionChange = (section) => {
        setSeccioActiva(section);
        setIsEditing(false);
        setDraftData(formData);
    };

    const createEmptyGuest = (id, isMainGuest = false) => ({
        id,
        isMainGuest,
        fullName: '',
        gender: '',
        relationship: '',
        documentType: '',
        documentNumber: '',
        nationality: '',
        birthDate: '',
        residence: '',
        email: '',
        phone: '',
    });

    const handleGuestChange = (guestId, e) => {
    const { name, value } = e.target;

    setDraftHostesData((prev) => ({
        ...prev,
        guests: prev.guests.map((guest) =>
        guest.id === guestId ? { ...guest, [name]: value } : guest
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
                    (_, index) =>
                    createEmptyGuest(
                        Date.now() + index,
                        false
                    ));
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

                return {
                    ...prev,
                    guestCount: newCount,
                };
            }

            return {
                ...prev,
                guestCount: newCount,
            };
        });
    };

    const handleSelectGuestToRemove = (guestId) => {
        setPendingGuestRemoval((prev) => ({
            ...prev,
            selectedGuestId: guestId,
        }));
    };

    const handleConfirmGuestRemoval = () => {
        setDraftHostesData((prev) => {
            const filteredGuests = prev.guests.filter(
            (guest) => guest.id !== pendingGuestRemoval.selectedGuestId
            );

            const updatedGuests = filteredGuests.map((guest, index) => ({
            ...guest,
            isMainGuest: index === 0,
            }));

            return {
            guestCount: pendingGuestRemoval.targetCount,
            guests: updatedGuests,
            };
        });
        setPendingGuestRemoval({
            isPending: false,
            targetCount: null,
            selectedGuestId: null,
        });
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

    return(
     <section>
        <div  className={style.templateGrid}>
            <Sidebar setSeccioActiva={setSeccioActiva} seccioActiva={seccioActiva} />
            <div className={style.perfilCard}>
                {seccioActiva === 'info' && (
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
                {seccioActiva === 'hospedes' && (
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
                {seccioActiva === 'pagaments' && <div><h2>Pagaments</h2></div>}

                {(seccioActiva === 'info' || seccioActiva === 'hospedes') && (
                    <PageFooterActions
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
};