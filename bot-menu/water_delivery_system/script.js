// Data Storage and Management (using localStorage)
const STORAGE_KEY = 'waterDeliveryData';

let appData = {
    customers: [],
    routes: [],
    products: [
        { id: 'prod-1', name: 'Bidón 20L', price: 500, stock: 100 },
        { id: 'prod-2', name: 'Bidón 10L', price: 300, stock: 150 },
        { id: 'prod-3', name: 'Soda 1.5L', price: 150, stock: 200 },
        { id: 'prod-4', name: 'Agua saborizada 0.5L', price: 100, stock: 300 }
    ],
    deliveries: [], // { customerId, routeId, date, products: [{id, qty}], status: 'pending'/'delivered'/'canceled' }
    debts: [] // { customerId, amount, date, description }
};

function loadData() {
    const storedData = localStorage.getItem(STORAGE_KEY);
    if (storedData) {
        appData = JSON.parse(storedData);
        // Ensure products have default stock if not present (for initial setup)
        appData.products.forEach(p => {
            if (typeof p.stock === 'undefined') p.stock = 0;
        });
        console.log('Data loaded from localStorage:', appData);
    } else {
        console.log('No data found in localStorage, using initial appData.');
    }
}

function saveData() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(appData));
    console.log('Data saved to localStorage.');
}

// Initialize some dummy data if localStorage is empty
function initializeDummyData() {
    if (!localStorage.getItem(STORAGE_KEY)) {
        appData.customers = [
            { id: 'cust-1', name: 'Juan Perez', address: 'Calle Falsa 123', phone: '3764112233', debt: 0, notes: 'Cliente frecuente, siempre paga en efectivo.' },
            { id: 'cust-2', name: 'Maria Lopez', address: 'Av. Siempreviva 742', phone: '3764445566', debt: 700, notes: 'Debe 1 bidón 20L del mes pasado.' },
            { id: 'cust-3', name: 'Carlos Gomez', address: 'Pasaje Seguro 88', phone: '3764778899', debt: 0, notes: 'Nuevo cliente.' },
            { id: 'cust-4', name: 'Ana Rodriguez', address: 'Ruta 12 Km 5', phone: '3764123456', debt: 300, notes: 'Debe 1 bidón 10L.' }
        ];

        appData.routes = [
            { id: 'route-1', name: 'Ruta Norte', customers: ['cust-1', 'cust-3'], driver: 'Pedro' },
            { id: 'route-2', name: 'Ruta Sur', customers: ['cust-2', 'cust-4'], driver: 'Maria' }
        ];

        appData.deliveries = [
            { id: 'del-1', customerId: 'cust-1', routeId: 'route-1', date: '2026-01-23', products: [{id: 'prod-1', qty: 1}], status: 'delivered' },
            { id: 'del-2', customerId: 'cust-2', routeId: 'route-2', date: '2026-01-23', products: [{id: 'prod-1', qty: 1}, {id: 'prod-3', qty: 2}], status: 'pending' },
            { id: 'del-3', customerId: 'cust-3', routeId: 'route-1', date: '2026-01-23', products: [{id: 'prod-2', qty: 1}], status: 'pending' }
        ];

        appData.debts = [
            { id: 'debt-1', customerId: 'cust-2', amount: 700, date: '2026-01-15', description: 'Bidón 20L pendiente' },
            { id: 'debt-2', customerId: 'cust-4', amount: 300, date: '2026-01-20', description: 'Bidón 10L pendiente' }
        ];
        saveData();
    }
}


// --- CRUD Operations ---

// Customers
function addCustomer(customer) {
    customer.id = 'cust-' + Date.now();
    customer.debt = 0; // New customers start with no debt
    appData.customers.push(customer);
    saveData();
}

function updateCustomer(updatedCustomer) {
    const index = appData.customers.findIndex(c => c.id === updatedCustomer.id);
    if (index !== -1) {
        appData.customers[index] = { ...appData.customers[index], ...updatedCustomer };
        saveData();
    }
}

function deleteCustomer(id) {
    appData.customers = appData.customers.filter(c => c.id !== id);
    // Also remove from routes and deliveries
    appData.routes.forEach(route => {
        route.customers = route.customers.filter(cId => cId !== id);
    });
    appData.deliveries = appData.deliveries.filter(d => d.customerId !== id);
    appData.debts = appData.debts.filter(d => d.customerId !== id);
    saveData();
}

function getCustomerById(id) {
    return appData.customers.find(c => c.id === id);
}

// Routes
function addRoute(route) {
    route.id = 'route-' + Date.now();
    route.customers = route.customers || []; // Ensure customers array exists
    appData.routes.push(route);
    saveData();
}

function updateRoute(updatedRoute) {
    const index = appData.routes.findIndex(r => r.id === updatedRoute.id);
    if (index !== -1) {
        appData.routes[index] = { ...appData.routes[index], ...updatedRoute };
        saveData();
    }
}

function deleteRoute(id) {
    appData.routes = appData.routes.filter(r => r.id !== id);
    appData.deliveries = appData.deliveries.filter(d => d.routeId !== id); // Remove associated deliveries
    saveData();
}

function getRouteById(id) {
    return appData.routes.find(r => r.id === id);
}

// Products
function addProduct(product) {
    product.id = 'prod-' + Date.now();
    appData.products.push(product);
    saveData();
}

function updateProduct(updatedProduct) {
    const index = appData.products.findIndex(p => p.id === updatedProduct.id);
    if (index !== -1) {
        appData.products[index] = { ...appData.products[index], ...updatedProduct };
        saveData();
    }
}

function deleteProduct(id) {
    appData.products = appData.products.filter(p => p.id !== id);
    // Consider how to handle products in old deliveries - perhaps mark as 'deleted' or keep a historical record
    saveData();
}

function getProductById(id) {
    return appData.products.find(p => p.id === id);
}

// Deliveries
function addDelivery(delivery) {
    delivery.id = 'del-' + Date.now();
    appData.deliveries.push(delivery);
    saveData();
}

function updateDelivery(updatedDelivery) {
    const index = appData.deliveries.findIndex(d => d.id === updatedDelivery.id);
    if (index !== -1) {
        appData.deliveries[index] = { ...appData.deliveries[index], ...updatedDelivery };
        saveData();
    }
}

function deleteDelivery(id) {
    appData.deliveries = appData.deliveries.filter(d => d.id !== id);
    saveData();
}

// Debts
function addDebt(debt) {
    debt.id = 'debt-' + Date.now();
    appData.debts.push(debt);
    const customer = getCustomerById(debt.customerId);
    if (customer) {
        customer.debt = (customer.debt || 0) + debt.amount;
        updateCustomer(customer); // This will save data
    } else {
        saveData();
    }
}

function recordPayment(debtId, paymentAmount) {
    const debtIndex = appData.debts.findIndex(d => d.id === debtId);
    if (debtIndex !== -1) {
        const debt = appData.debts[debtIndex];
        const customer = getCustomerById(debt.customerId);

        if (customer) {
            customer.debt = (customer.debt || 0) - paymentAmount;
            if (customer.debt < 0) customer.debt = 0; // Avoid negative debt
            updateCustomer(customer);
        }
        // For simplicity, we just reduce the customer's overall debt.
        // A more complex system would track individual debt items.
        appData.debts = appData.debts.filter(d => d.id !== debtId); // Remove specific debt item
        saveData(); // Save changes after updating customer and removing debt item
    }
}


// --- Helper Functions for UI ---
function getCustomerName(customerId) {
    const customer = getCustomerById(customerId);
    return customer ? customer.name : 'Desconocido';
}

function getProductName(productId) {
    const product = getProductById(productId);
    return product ? product.name : 'Desconocido';
}

function getRouteName(routeId) {
    const route = getRouteById(routeId);
    return route ? route.name : 'Desconocido';
}

// --- Mobile Menu Toggle ---
document.addEventListener('DOMContentLoaded', () => {
    const mobileMenuToggle = document.getElementById('mobile-menu');
    const nav = document.getElementById('nav');

    if (mobileMenuToggle && nav) {
        mobileMenuToggle.addEventListener('click', () => {
            nav.classList.toggle('nav-open');
            mobileMenuToggle.classList.toggle('active');
        });
    }

    // Load data when script is loaded
    loadData();
    initializeDummyData(); // Only initializes if no data is found
});
