import sqlite3

def create_db_connection(db_path='pos_system.db'):
    conn = sqlite3.connect(db_path)
    return conn

def initialize_db():
    conn = create_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            notes TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            ticket_type TEXT NOT NULL,
            pieces INTEGER NOT NULL,
            notes TEXT,
            due_date TEXT,
            overall_notes TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS garments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER,
            name TEXT NOT NULL,
            variation TEXT,
            color TEXT,
            pattern TEXT,
            texture TEXT,
            upcharges TEXT,
            FOREIGN KEY (ticket_id) REFERENCES tickets (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quick_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            due_date TEXT NOT NULL,
            overall_notes TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quick_ticket_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quick_ticket_id INTEGER NOT NULL,
            ticket_type TEXT NOT NULL,
            pieces INTEGER NOT NULL,
            notes TEXT,
            FOREIGN KEY (quick_ticket_id) REFERENCES quick_tickets(id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_db()
