const express = require('express');
const { connectDb, initializeDb, getDb } = require('./database');
const cors = require('cors');
const fetch = require('node-fetch'); // Import node-fetch

const app = express();
const PORT = 3001; // Choose a different port than the bot itself
const BOT_PAGINA_URL = 'http://localhost:5000'; // Assuming bot-pagina runs on port 5000

app.use(express.json()); // For parsing application/json
app.use(cors()); // Enable CORS for all routes

// Initialize database and start server
async function startServer() {
    try {
        await connectDb();
        await initializeDb();
        
        app.listen(PORT, () => {
            console.log(`Backend server running on http://localhost:${PORT}`);
        });
    } catch (error) {
        console.error('Failed to start backend server:', error);
        process.exit(1);
    }
}

// Basic API routes (will be expanded)
app.get('/api/status', (req, res) => {
    res.json({ message: 'Backend is running!', database: 'connected' });
});

// Get all conversations (contacts with last message and intervention status)
app.get('/api/conversations', (req, res) => {
    const db = getDb();
    const query = `
        SELECT
            c.id AS contact_id,
            c.phone_number,
            c.name,
            conv.is_human_intervening,
            MAX(m.timestamp) AS last_message_timestamp,
            (SELECT content FROM messages WHERE contact_id = c.id ORDER BY timestamp DESC LIMIT 1) AS last_message_content
        FROM contacts c
        LEFT JOIN conversations conv ON c.id = conv.contact_id
        LEFT JOIN messages m ON c.id = m.contact_id
        GROUP BY c.id
        ORDER BY last_message_timestamp DESC;
    `;
    db.all(query, [], (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json(rows);
    });
});

// Get messages for a specific conversation
app.get('/api/conversations/:phoneNumber/messages', (req, res) => {
    const db = getDb();
    const phoneNumber = req.params.phoneNumber;
    const query = `
        SELECT
            m.id,
            m.sender,
            m.message_type,
            m.content,
            m.timestamp
        FROM messages m
        JOIN contacts c ON m.contact_id = c.id
        WHERE c.phone_number = ?
        ORDER BY m.timestamp ASC;
    `;
    db.all(query, [phoneNumber], (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json(rows);
    });
});

// Set human intervention status
app.post('/api/conversations/:phoneNumber/intervene', (req, res) => {
    const db = getDb();
    const { status } = req.body; // status: true or false
    const phoneNumber = req.params.phoneNumber;

    if (typeof status !== 'boolean') {
        return res.status(400).json({ error: 'Status must be a boolean (true/false).' });
    }

    db.run(
        `UPDATE conversations
         SET is_human_intervening = ?, last_updated = CURRENT_TIMESTAMP
         WHERE contact_id = (SELECT id FROM contacts WHERE phone_number = ?)`,
        [status ? 1 : 0, phoneNumber],
        function (err) {
            if (err) {
                res.status(500).json({ error: err.message });
                return;
            }
            if (this.changes === 0) {
                // If no row was updated, it means the conversation or contact doesn't exist.
                // We should ensure they exist before calling this, or create them here.
                // For simplicity now, we assume they exist due to message logging.
                // In a real app, you might want to create them if not found.
                 res.status(404).json({ message: 'Conversation not found for this phone number, or no change in status.' });
                 return;
            }
            res.json({ message: `Intervention status for ${phoneNumber} set to ${status}.` });
        }
    );
});

// Send a message from the dashboard (as a human)
app.post('/api/messages/send', async (req, res) => {
    const db = getDb();
    const { phoneNumber, content } = req.body;

    if (!phoneNumber || !content) {
        return res.status(400).json({ error: 'Phone number and message content are required.' });
    }

    try {
        // Record the message in the database as 'human' (sent from dashboard)
        db.run(
            `INSERT INTO contacts (phone_number) VALUES (?) ON CONFLICT(phone_number) DO NOTHING`,
            [phoneNumber]
        );
        const contactIdQuery = await new Promise((resolve, reject) => {
            db.get(`SELECT id FROM contacts WHERE phone_number = ?`, [phoneNumber], (err, row) => {
                if (err) reject(err);
                else resolve(row);
            });
        });
        const contact_id = contactIdQuery.id;

        db.run(
            `INSERT INTO messages (contact_id, sender, message_type, content, timestamp) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)`,
            [contact_id, 'human', 'text', content],
            function (err) {
                if (err) {
                    throw err;
                }
                console.log(`Message recorded in DB from dashboard for ${phoneNumber}.`);
            }
        );

        // Call bot-pagina's endpoint to send the message
        const botResponse = await fetch(`${BOT_PAGINA_URL}/api/send_message_from_dashboard`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone_number: phoneNumber, message: content })
        });

        if (!botResponse.ok) {
            const errorText = await botResponse.text();
            throw new Error(`Bot-pagina failed to send message: ${botResponse.status} - ${errorText}`);
        }

        const botResponseJson = await botResponse.json();
        console.log(`Message successfully relayed to bot-pagina:`, botResponseJson);
        
        // Update conversation's last_updated timestamp
        db.run(
            `UPDATE conversations SET last_updated = CURRENT_TIMESTAMP WHERE contact_id = ?`,
            [contact_id],
            function (err) {
                if (err) {
                    console.error("Error updating conversation timestamp:", err.message);
                }
            }
        );

        res.json({ status: 'success', message: 'Message sent via bot-pagina and recorded.', phoneNumber, content });
    } catch (error) {
        console.error('Error sending message from dashboard:', error);
        res.status(500).json({ error: error.message });
    }
});

startServer();
