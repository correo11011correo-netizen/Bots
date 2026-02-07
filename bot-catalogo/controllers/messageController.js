
const mainMenu = require('../menu/principal');
const submenus = require('../menu/submenus');
const whatsappService = require('../services/whatsappService');

let userState = {}; // Almacenar el estado del usuario (en qué menú se encuentra)

const handleMessage = (req, res) => {
  const body = req.body;
  if (body.object !== 'whatsapp_business_account') {
    return res.sendStatus(404);
  }

  const message = body.entry?.[0]?.changes?.[0]?.value?.messages?.[0];
  if (!message || !message.text) {
    return res.sendStatus(200); // Not a message we can handle
  }

  const from = message.from; // Sender's phone number
  const messageText = message.text.body.toLowerCase();

  const currentState = userState[from] || 'main';

  if (currentState === 'main') {
    if (mainMenu[messageText]) {
      const selectedOption = mainMenu[messageText];
      if (selectedOption.submenu) {
        userState[from] = selectedOption.submenu;
        // Enviar el submenú
        const submenuText = getTextForMenu(submenus[selectedOption.submenu]);
        whatsappService.sendMessage(from, submenuText);
      } else {
        // Ejecutar la acción
        executeAction(from, selectedOption.action);
      }
    } else {
      // Enviar el menú principal si la opción no es válida
      const menuText = getTextForMenu(mainMenu);
      whatsappService.sendMessage(from, `Opción no válida. Por favor, elige una de las siguientes opciones:\n\n${menuText}`);
    }
  } else {
    // Lógica para manejar los submenús
    const currentSubmenu = submenus[currentState];
    if (currentSubmenu && currentSubmenu[messageText]) {
      const selectedOption = currentSubmenu[messageText];
      if (selectedOption.submenu) {
        userState[from] = selectedOption.submenu;
        const submenuText = getTextForMenu(submenus[selectedOption.submenu]);
        whatsappService.sendMessage(from, submenuText);
      } else if (selectedOption.action === 'returnToMainMenu') {
        userState[from] = 'main';
        const menuText = getTextForMenu(mainMenu);
        whatsappService.sendMessage(from, menuText);
      }
      else {
        executeAction(from, selectedOption.action);
      }
    } else {
      const submenuText = getTextForMenu(currentSubmenu);
      whatsappService.sendMessage(from, `Opción no válida. Por favor, elige una de las siguientes opciones:\n\n${submenuText}`);
    }
  }

  res.sendStatus(200);
};

const getTextForMenu = (menu) => {
  let menuText = '';
  for (const key in menu) {
    menuText += `${key}. ${menu[key].text}\n`;
  }
  return menuText;
};

const executeAction = (user, action) => {
  // Aquí se ejecutarían las acciones específicas
  console.log(`Ejecutando la acción "${action}" para el usuario ${user}`);
  // Por ejemplo, podrías tener un switch o un objeto que mapee acciones a funciones
  switch (action) {
    case 'talkToRepresentative':
      whatsappService.sendMessage(user, 'En un momento un representante se pondrá en contacto contigo.');
      break;
    case 'checkOrderStatus':
      whatsappService.sendMessage(user, 'Por favor, ingresa tu número de pedido.');
      break;
    // ... más acciones
  }
};


module.exports = {
  handleMessage,
};
