const db = require('./DB');
const bcrypt = require('bcrypt');
async function register(nom,email,rol,NIP, password)
{
    try {
        const password_hash = await bcrypt.hash(password, 10);
        const result = await db.query(
            'INSERT INTO usuari (nom, email, password_hash, rol, nip) VALUES ($1, $2, $3, $4, $5) RETURNING *',
            [nom,email,password_hash,rol,NIP]
        );
        return result.rows[0];
    } catch (err) {
        console.error('Error al registrar usuario:', err);
        throw err; 
    }
}

async function login(email,password) {
    try {
        const result = await db.query('SELECT * FROM usuari WHERE email = $1', [email]);
        if (result.rows.length === 0) {
            throw new Error('Usuario no encontrado');
        }
        const user = result.rows[0];
        const isMatch = await bcrypt.compare(password, user.password_hash);
        if (!isMatch) {
            throw new Error('Contraseña incorrecta');
        }
        return user;
    } catch (err) {
        console.error('Error al iniciar sesión:', err);
        throw err;
    }
}


(async () => {
    try {
        const result = await login("arnau.tv2@gmail.com", "password");
        console.log('login correcte', result);
    } catch (err) {
        console.error('error', err.message);
    }
})();