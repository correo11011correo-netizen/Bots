
const submenus = {
  products: {
    1: {
      text: 'Volver al menú principal',
      action: 'returnToMainMenu',
    },
    2: {
      text: 'Ver categoría A',
      submenu: 'categoryA',
    },
    3: {
      text: 'Ver categoría B',
      submenu: 'categoryB',
    },
  },
  categoryA: {
    1: {
      text: 'Volver al menú de productos',
      submenu: 'products',
    },
    2: {
      text: 'Producto 1',
      action: 'showProduct1',
    },
  },
  categoryB: {
    1: {
      text: 'Volver al menú de productos',
      submenu: 'products',
    },
    2: {
      text: 'Producto 2',
      action: 'showProduct2',
    },
  },
};

module.exports = submenus;
