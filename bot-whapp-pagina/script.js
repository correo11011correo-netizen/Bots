document.addEventListener('DOMContentLoaded', () => {
    // --- Globals ---
    let currentContact = null;
// Use the API_BASE_URL injected by the server in index.html
    const API_BASE_URL = window.API_BASE_URL.replace(/"/g, '');

    // --- DOM Elements ---
    const conversationList = document.getElementById('conversation-list');
    const chatView = document.getElementById('chat-view');
    const chatHeader = document.getElementById('chat-header');
    const chatMessages = document.getElementById('chat-messages');
    const messageInputContainer = document.getElementById('chat-input-container');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    // Debug elements
    const testButton = document.getElementById('test-button');
    const logOutput = document.getElementById('log-output');

    // --- Debug Functions ---
    function logToScreen(message) {
        console.log(message); // Also log to console for good measure
        logOutput.textContent += `[${new Date().toLocaleTimeString()}] ${message}\n`;
        logOutput.scrollTop = logOutput.scrollHeight;
    }

    async function runApiTest() {
        logToScreen("--- Iniciando Test de API ---");
        const url = `${API_BASE_URL}/api/conversations`;
        logToScreen(`1. URL del Fetch: ${url}`);
        
        try {
            logToScreen("2. Realizando petición fetch...");
            const response = await fetch(url);
            logToScreen(`3. Respuesta recibida. Status: ${response.status} ${response.statusText}`);
            
            const headers = {};
            response.headers.forEach((value, key) => {
                headers[key] = value;
            });
            logToScreen(`4. Cabeceras de la respuesta:\n${JSON.stringify(headers, null, 2)}`);

            logToScreen("5. Leyendo cuerpo de la respuesta como texto plano...");
            const rawText = await response.text();
            logToScreen(`6. Respuesta en texto plano (RAW):\n---\n${rawText}\n---`);

            logToScreen("7. Intentando parsear texto como JSON...");
            const jsonData = JSON.parse(rawText);
            logToScreen("8. ¡Éxito! El JSON es válido.");
            logToScreen(`9. Chats encontrados: ${jsonData.length}`);
        } catch (error) {
            logToScreen(`--- ¡ERROR! ---`);
            logToScreen(error.toString());
            logToScreen(`Stack Trace: ${error.stack}`);
        }
    }


    // --- Core Functions ---

    function renderMessage(msg) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', msg.sender.toLowerCase());
        const senderLabel = document.createElement('div');
        senderLabel.classList.add('sender-label');
        if (msg.sender.toLowerCase() === 'human') senderLabel.textContent = 'Tú (Manual)';
        else if (msg.sender.toLowerCase() === 'bot') senderLabel.textContent = 'Bot';
        
        const contentElement = document.createElement('p');
        contentElement.textContent = msg.content;
        const timestampElement = document.createElement('span');
        timestampElement.classList.add('timestamp');
        const date = new Date(msg.timestamp);
        timestampElement.textContent = date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });

        if(senderLabel.textContent) messageElement.appendChild(senderLabel);
        messageElement.appendChild(contentElement);
        messageElement.appendChild(timestampElement);
        chatMessages.appendChild(messageElement);
    }

    async function loadMessages(phoneNumber) {
        chatMessages.innerHTML = 'Cargando mensajes...';
        try {
            const response = await fetch(`${API_BASE_URL}/api/messages/${phoneNumber}`);
            if (!response.ok) throw new Error(`Error del servidor: ${response.status}`);
            const messages = await response.json();
            chatMessages.innerHTML = '';
            messages.forEach(renderMessage);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } catch (error) {
            logToScreen(`Error en loadMessages: ${error.message}`);
            chatMessages.innerHTML = `<div class="message client"><p>Error al cargar mensajes. ${error.message}</p></div>`;
        }
    }

    function selectConversation(contact, conversationElement) {
        currentContact = contact;
        chatHeader.innerHTML = `<h3>${contact.name || contact.phone_number}</h3>`;
        messageInputContainer.style.display = 'flex';
        document.querySelectorAll('.conversation-item').forEach(el => el.classList.remove('selected'));
        conversationElement.classList.add('selected');
        loadMessages(contact.phone_number);
    }

    async function loadConversations() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/conversations`);
            if (!response.ok) {
                 throw new Error(`Respuesta del servidor no fue OK: ${response.status}`);
            }
            const conversations = await response.json();
            conversationList.innerHTML = ''; 

            if (conversations.length === 0) {
                conversationList.innerHTML = '<div class="conversation-item"><p>No hay conversaciones.</p></div>';
                return;
            }

            conversations.forEach(conv => {
                const item = document.createElement('div');
                item.classList.add('conversation-item');
                item.dataset.phoneNumber = conv.phone_number;
                const name = conv.name || conv.phone_number;
                const lastMessage = conv.last_message_content || 'No hay mensajes.';
                const status = conv.is_human_intervening ? 'HUMANO' : 'BOT';
                item.innerHTML = `<h4>${name}</h4><p>${lastMessage}</p><p class="status ${status.toLowerCase()}">Modo: ${status}</p>`;
                item.addEventListener('click', () => selectConversation(conv, item));
                conversationList.appendChild(item);
            });
        } catch (error) {
            logToScreen(`Error en loadConversations: ${error.message}`);
            conversationList.innerHTML = `<div class="conversation-item"><p>Error al cargar chats. Revisa la consola de debug.</p></div>`;
        }
    }

    async function sendManualMessage() {
        const messageText = messageInput.value.trim();
        if (!messageText || !currentContact) return;
        try {
            const response = await fetch(`${API_BASE_URL}/api/send_message_from_dashboard`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    phone_number: currentContact.phone_number,
                    message: messageText
                })
            });
            if (!response.ok) throw new Error(`Error del servidor: ${response.status}`);
            messageInput.value = '';
            setTimeout(() => { loadMessages(currentContact.phone_number); }, 500);
        } catch (error) {
            logToScreen(`Error en sendManualMessage: ${error.message}`);
        }
    }

    // --- Event Listeners ---
    sendButton.addEventListener('click', sendManualMessage);
    messageInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendManualMessage(); });
    testButton.addEventListener('click', runApiTest);

    // --- Initial Load ---
    loadConversations();
});
