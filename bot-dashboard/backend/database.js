const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const DB_PATH = path.resolve(__dirname, 'bot_dashboard.db');
let db;

function connectDb() {
    return new Promise((resolve, reject) => {
        db = new sqlite3.Database(DB_PATH, (err) => {
            if (err) {
                console.error('Error connecting to database:', err.message);
                return reject(err);
            }
            console.log('Connected to the SQLite database.');
            resolve(db);
        });
    });
}

function initializeDb() {
    return new Promise(async (resolve, reject) => {
        try {
            if (!db) {
                await connectDb();
            }

            db.serialize(() => {
                db.run(`CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT UNIQUE NOT NULL,
                    name TEXT,
                    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
                )`, (err) => {
                    if (err) {
                        console.error('Error creating contacts table:', err.message);
                        return reject(err);
                    }
                    console.log('Contacts table ensured.');
                });

                db.run(`CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER NOT NULL,
                    sender TEXT NOT NULL, -- 'bot' or 'client' or 'human'
                    message_type TEXT NOT NULL, -- 'text', 'image', 'audio', etc.
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contact_id) REFERENCES contacts (id)
                )`, (err) => {
                    if (err) {
                        console.error('Error creating messages table:', err.message);
                        return reject(err);
                    }
                    console.log('Messages table ensured.');
                });

                db.run(`CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER UNIQUE NOT NULL,
                    is_human_intervening BOOLEAN DEFAULT 0, -- 0 for false, 1 for true
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contact_id) REFERENCES contacts (id)
                )`, (err) => {
                    if (err) {
                        console.error('Error creating conversations table:', err.message);
                        return reject(err);
                    }
                    console.log('Conversations table ensured.');
                    resolve();
                });
            });
        } catch (err) {
            reject(err);
        }
    });
}

function getDb() {
    if (!db) {
        throw new Error("Database not connected. Call connectDb() and initializeDb() first.");
    }
    return db;
}

module.exports = {
    connectDb,
    initializeDb,
    getDb
};
