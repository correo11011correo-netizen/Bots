import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://100.114.190.117:3001/api';

function App() {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch all conversations
  useEffect(() => {
    fetchConversations();
    // Refresh conversations every 10 seconds
    const interval = setInterval(fetchConversations, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchConversations = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/conversations`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setConversations(data);
      setLoading(false);
    } catch (err) {
      setError(err);
      setLoading(false);
      console.error("Error fetching conversations:", err);
    }
  };

  // Fetch messages for selected conversation
  useEffect(() => {
    if (selectedConversation) {
      fetchMessages(selectedConversation.phone_number);
      const interval = setInterval(() => fetchMessages(selectedConversation.phone_number), 5000);
      return () => clearInterval(interval);
    } else {
      setMessages([]);
    }
  }, [selectedConversation]);

  const fetchMessages = async (phoneNumber) => {
    try {
      const response = await fetch(`${API_BASE_URL}/conversations/${phoneNumber}/messages`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setMessages(data);
    } catch (err) {
      console.error("Error fetching messages:", err);
    }
  };

  const handleSelectConversation = (conversation) => {
    setSelectedConversation(conversation);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedConversation) return;

    try {
      const response = await fetch(`${API_BASE_URL}/messages/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phoneNumber: selectedConversation.phone_number,
          content: newMessage,
          senderType: 'human', // Sent by the human agent
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      setNewMessage('');
      fetchMessages(selectedConversation.phone_number); // Refresh messages after sending
    } catch (err) {
      console.error("Error sending message:", err);
      alert("Error sending message. Check console for details.");
    }
  };

  const toggleIntervention = async () => {
    if (!selectedConversation) return;
    const newStatus = !selectedConversation.is_human_intervening;

    try {
      const response = await fetch(`${API_BASE_URL}/conversations/${selectedConversation.phone_number}/intervene`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Update the local state for the selected conversation
      setSelectedConversation((prev) => ({
        ...prev,
        is_human_intervening: newStatus,
      }));
      // Also refresh the main conversations list to reflect the change
      fetchConversations();
      alert(`Intervention status for ${selectedConversation.phone_number} set to ${newStatus}.`);
    } catch (err) {
      console.error("Error toggling intervention status:", err);
      alert("Error toggling intervention status. Check console for details.");
    }
  };

  if (loading) return <div className="app-container">Loading conversations...</div>;
  if (error) return <div className="app-container">Error: {error.message}</div>;

  return (
    <div className="app-container">
      <div className="conversations-panel">
        <div className="panel-header">
          <h2>Conversaciones</h2>
        </div>
        <ul className="conversation-list">
          {conversations.map((conv) => (
            <li
              key={conv.contact_id}
              className={`conversation-item ${selectedConversation?.contact_id === conv.contact_id ? 'active' : ''}`}
              onClick={() => handleSelectConversation(conv)}
            >
              <div className="conversation-info">
                <h3>{conv.name || conv.phone_number}</h3>
                <p>{conv.last_message_content}</p>
              </div>
              <div className="conversation-meta">
                {conv.is_human_intervening ? <span className="intervention-tag">HUMANO</span> : null}
                {/* <p>{new Date(conv.last_message_timestamp).toLocaleTimeString()}</p> */}
              </div>
            </li>
          ))}
        </ul>
      </div>

      <div className="chat-panel">
        {selectedConversation ? (
          <>
            <div className="panel-header">
              <h2>{selectedConversation.name || selectedConversation.phone_number}</h2>
              <button
                onClick={toggleIntervention}
                className="toggle-intervention-button"
              >
                {selectedConversation.is_human_intervening ? 'Bot Activo' : 'Intervenir'}
              </button>
            </div>
            <div className="messages-container">
                {messages.slice().reverse().map((msg) => ( // Reverse to display newest at bottom
                  <div key={msg.id} className={`message-bubble ${msg.sender}`}>
                    <div className="message-sender">{msg.sender === 'client' ? 'Cliente' : (msg.sender === 'bot' ? 'Bot' : 'Tú')}</div>
                    {msg.content}
                    <div className="message-time">{new Date(msg.timestamp).toLocaleString()}</div>
                  </div>
                ))}
            </div>
            <form onSubmit={handleSendMessage} className="chat-input-area">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Escribe un mensaje..."
              />
              <button type="submit">Enviar</button>
            </form>
          </>
        ) : (
          <div className="empty-chat-panel">
            Selecciona una conversación para empezar.
          </div>
        )}
      </div>
    </div>
  );
}

export default App;