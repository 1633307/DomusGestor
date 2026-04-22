import {useState} from 'react';
import Sidebar from '../layout/Sidebar';
import style from './InfoReservaPage.module.css';


export default function InfoReserva(infoActiva,setInfoActiva){

    const [seccioActiva, setSeccioActiva] = useState('info');

    return(
     <section>
        <div  className={style.templateGrid}>
            <Sidebar setSeccioActiva={setSeccioActiva} seccioActiva={seccioActiva} />
            <div className={style.perfilCard}>
                {seccioActiva === 'info' && <div><h2>Informació reserva</h2></div>}
                {seccioActiva === 'hospedes' && <div><h2>Hospedes</h2></div>}
                {seccioActiva === 'pagaments' && <div><h2>Pagaments</h2></div>}
            </div>
        </div>
    </section>
    );
};