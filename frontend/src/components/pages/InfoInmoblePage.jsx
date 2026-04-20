import {useState} from 'react';
import Sidebar from '../layout/Sidebar';
import style from './InfoInmoblePage.module.css';


export default function InfoInmoble(){

    const [seccioActiva, setSeccioActiva] = useState('perfil');

    return(
     <section>
        <div  className={style.templateGrid}>
            <Sidebar setSeccioActiva={setSeccioActiva} seccioActiva={seccioActiva} />
            <div className={style.perfilCard}>
                {seccioActiva === 'perfil' && <div><h2>Perfil de l'immoble</h2></div>}
                {seccioActiva === 'fotos' && <div><h2>Galeria de Fotos</h2></div>}
                {seccioActiva === 'incidencies' && <div><h2>Gestió d'Incidències</h2></div>}
            </div>
        </div>
    </section>
    );
};