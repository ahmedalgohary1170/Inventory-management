import sqlite3
import os
from pathlib import Path

DEFAULT_DB_NAME = "installments.db"
DB_PATH = None

class Database:
    _instance = None
    
    @classmethod
    def set_db_path(cls, db_path):
        global DB_PATH
        DB_PATH = db_path
        # Reset the instance to force reinitialization with new path
        cls._instance = None
    
    def __new__(cls, db_path=None):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.initialized = False
            
            # Determine the database path
            final_path = db_path or DB_PATH or DEFAULT_DB_NAME
            final_path = os.path.abspath(final_path)
            
            # Create parent directory if it doesn't exist
            db_dir = os.path.dirname(final_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            # Set the instance's db_path to the absolute path
            cls._instance.db_path = final_path
            cls._instance.conn = sqlite3.connect(final_path)
            cls._instance.conn.row_factory = sqlite3.Row
            cls._instance.create_tables()
            cls._instance.initialized = True
            
            # Print for debugging
            print(f"Database initialized at: {final_path}")
            
        return cls._instance
        
    def __init__(self, db_path=None):
        if not self.initialized:
            # This should not normally be reached due to __new__
            final_path = db_path or DB_PATH or DEFAULT_DB_NAME
            self.db_path = os.path.abspath(final_path)
            
            # Create parent directory if it doesn't exist
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.create_tables()
            self.initialized = True

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
        
        # First, create a new invoices table with all required columns
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS invoices_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            product_id INTEGER,
            quantity REAL,
            total_amount REAL,
            upfront_paid REAL DEFAULT 0,
            installment_count INTEGER DEFAULT 0,
            installment_amount REAL,
            start_date TEXT,
            invoice_date TEXT DEFAULT (date('now')),
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(customer_id) REFERENCES customers(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )""")
        
        # Handle migration from old schema to new schema
        try:
            # Check if we have the new table structure
            cursor = self.conn.execute("PRAGMA table_info(invoices)")
            current_columns = [row[1] for row in cursor.fetchall()]
            
            # List of all required columns and their types
            required_columns = {
                'id': 'INTEGER PRIMARY KEY',
                'customer_id': 'INTEGER',
                'product_id': 'INTEGER',
                'quantity': 'REAL',
                'total_amount': 'REAL',
                'upfront_paid': 'REAL DEFAULT 0',
                'installment_count': 'INTEGER DEFAULT 0',
                'installment_amount': 'REAL',
                'start_date': 'TEXT',
                'invoice_date': 'TEXT DEFAULT (date(\'now\'))',
                'created_at': 'TEXT DEFAULT (datetime(\'now\'))'
            }
            
            # Check if we need to migrate
            needs_migration = False
            for col in required_columns:
                if col not in current_columns:
                    needs_migration = True
                    break
            
            if needs_migration:
                print("Migrating invoices table to new schema...")
                
                # Create a backup of the old table
                self.conn.execute("DROP TABLE IF EXISTS invoices_old")
                self.conn.execute("ALTER TABLE invoices RENAME TO invoices_old")
                
                # Create the new table with all required columns
                create_sql = """
                CREATE TABLE invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER,
                    product_id INTEGER,
                    quantity REAL,
                    total_amount REAL,
                    upfront_paid REAL DEFAULT 0,
                    installment_count INTEGER DEFAULT 0,
                    installment_amount REAL,
                    start_date TEXT,
                    invoice_date TEXT DEFAULT (date('now')),
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY(customer_id) REFERENCES customers(id),
                    FOREIGN KEY(product_id) REFERENCES products(id)
                )
                """
                self.conn.execute(create_sql)
                
                # Copy data from old table to new table
                cursor = self.conn.execute("PRAGMA table_info(invoices_old)")
                old_columns = [row[1] for row in cursor.fetchall()]
                
                # Build column lists for the migration
                columns_to_copy = [col for col in required_columns.keys() if col in old_columns]
                columns_sql = ", ".join(columns_to_copy)
                
                # Add default values for missing columns
                for col in required_columns:
                    if col not in columns_to_copy and col != 'id':  # Don't include id in the insert
                        if required_columns[col].startswith("INTEGER"):
                            columns_sql += f", 0 as {col}"
                        elif required_columns[col].startswith("REAL"):
                            columns_sql += f", 0.0 as {col}"
                        else:
                            columns_sql += f", '' as {col}"
                
                # Perform the migration
                self.conn.execute(f"""
                INSERT INTO invoices ({', '.join(required_columns.keys())})
                SELECT {columns_sql}
                FROM invoices_old
                """)
                
                # Set default values for any remaining NULLs
                for col, col_type in required_columns.items():
                    if 'DEFAULT' in col_type and col != 'id':
                        default = col_type.split('DEFAULT')[-1].strip(" ()'")
                        self.conn.execute(f"""
                        UPDATE invoices 
                        SET {col} = {default} 
                        WHERE {col} IS NULL
                        """)
                
                # Drop the old table
                self.conn.execute("DROP TABLE IF EXISTS invoices_old")
                print("Successfully migrated invoices table to new schema")
                
        except Exception as e:
            print(f"Error migrating invoices table: {e}")
            self.conn.rollback()
            # If migration fails, ensure we still have a valid table
            self.conn.execute("DROP TABLE IF EXISTS invoices_new")
            # Create a fresh table if migration fails
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
                invoice_date TEXT DEFAULT (date('now')),
                quantity REAL,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY(customer_id) REFERENCES customers(id),
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
            """)
        
        # Verify and add any missing columns to the invoices table
        columns_to_add = [
            ("upfront_paid", "REAL DEFAULT 0"),
            ("installment_count", "INTEGER DEFAULT 0"),
            ("installment_amount", "REAL"),
            ("start_date", "TEXT"),
            ("invoice_date", "TEXT DEFAULT (date('now'))")
        ]
        
        # Get existing columns
        cursor = self.conn.execute("PRAGMA table_info(invoices)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        # Add any missing columns
        for column, column_type in columns_to_add:
            if column not in existing_columns:
                try:
                    self.conn.execute(f"ALTER TABLE invoices ADD COLUMN {column} {column_type}")
                    print(f"Added missing column: {column}")
                except sqlite3.OperationalError as e:
                    print(f"Error adding column {column}: {e}")
        
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

