const db = require('./DB');
console.log("Lo que hay dentro del archivo DB es:", db);

async function probarConexion() {
    try {
        console.log('--- Iniciando prueba de conexión ---');
        
        // 1. Probamos una consulta simple al sistema
        const tiempo = await db.query('SELECT NOW() as ahora');
        console.log('✅ Conexión básica: OK (Hora del servidor: ' + tiempo.rows[0].ahora + ')');

        // 2. Intentamos leer tu tabla de inmuebles
        const inmuebles = await db.query('SELECT * FROM immoble LIMIT 1');
        
        if (inmuebles.rows.length > 0) {
            console.log('✅ Lectura de tabla "immoble": OK');
            console.log('Datos del primer inmueble:', inmuebles.rows[0]);
        } else {
            console.log('✅ Conexión OK, pero la tabla "immoble" está vacía.');
        }

    } catch (err) {
        console.error('❌ Error en la prueba:');
        
        if (err.code === 'ECONNREFUSED') {
            console.error('No se pudo conectar. ¿Está el servicio "DomusGestor" encendido en DBngin?');
        } else if (err.code === '42P01') {
            console.error('La tabla "immoble" no existe en la base de datos configurada.');
        } else {
            console.error(err.message);
        }
    } finally {
        // Cerramos el proceso de Node
        process.exit();
    }
}

probarConexion();