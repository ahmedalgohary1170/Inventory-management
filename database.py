import sqlite3

DB_PATH = "installments.db"

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        # Create customers table
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            note TEXT
        )""")
        
        # Create products table
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0
        )""")
        
        # Create invoices table
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            product_id INTEGER,
            total_amount REAL,
            upfront_paid REAL DEFAULT 0,
            installment_count INTEGER,
            installment_amount REAL,
            start_date TEXT,
            quantity REAL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(customer_id) REFERENCES customers(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )""")
        
        # Add upfront_paid column if it doesn't exist
        try:
            self.conn.execute("ALTER TABLE invoices ADD COLUMN upfront_paid REAL DEFAULT 0")
        except sqlite3.OperationalError:
            # Column already exists, ignore the error
            pass
        
        # Create payments table
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            payment_date TEXT,
            amount REAL,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
        )""")
        
        # Create indexes separately
        self.conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_payments_invoice_id 
        ON payments(invoice_id)""")
        
        self.conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_payments_payment_date 
        ON payments(payment_date)""")
        
        self.conn.commit()

    def execute(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur

    def fetch_all(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()

