
// Importar las dependencias necesarias
const express = require('express');
const bodyParser = require('body-parser');
const messageController = require('./controllers/messageController');

// Cargar las variables de entorno
require('dotenv').config();

const app = express();
app.use(bodyParser.json());

// Endpoint para recibir los webhooks de WhatsApp
app.post('/webhook', messageController.handleMessage);

// Endpoint para que WhatsApp verifique el webhook
app.get('/webhook', (req, res) => {
  const verify_token = process.env.VERIFY_TOKEN;

  let mode = req.query['hub.mode'];
  let token = req.query['hub.verify_token'];
  let challenge = req.query['hub.challenge'];

  if (mode && token) {
    if (mode === 'subscribe' && token === verify_token) {
      console.log('WEBHOOK_VERIFIED');
      res.status(200).send(challenge);
    } else {
      res.sendStatus(403);
    }
  }
});

// Iniciar el servidor
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`El servidor está escuchando en el puerto ${PORT}`);
});
