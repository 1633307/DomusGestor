const { Pool } = require('pg');


const pool = new Pool({
  user: 'postgres',
  host: '127.0.0.1',
  database: 'postgres', 
  password: '',         
  port: 1234,           
});


pool.on('connect', () => {
  console.log('✅ Conectado a la base de datos de DBngin');
});

pool.on('error', (err) => {
  console.error('❌ Error inesperado en el pool de conexiones', err);
});

module.exports = {
  query: (text, params) => pool.query(text, params),
  pool 
};