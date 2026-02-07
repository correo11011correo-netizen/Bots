
const mainMenu = {
  1: {
    text: 'Ver catálogo de productos',
    submenu: 'products',
  },
  2: {
    text: 'Hablar con un representante',
    action: 'talkToRepresentative',
  },
  3: {
    text: 'Ver estado de mi pedido',
    action: 'checkOrderStatus',
  },
};

module.exports = mainMenu;
