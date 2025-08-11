import sqlite3
import os
from database import Database

def check_database_schema():
    db_path = os.path.expanduser("~/Documents/.installments.db")
    print(f"Checking database at: {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("\nTables in database:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Check invoices table structure
    print("\nInvoices table structure:")
    try:
        cursor.execute("PRAGMA table_info(invoices)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"- {col[1]} ({col[2]}) {'DEFAULT ' + str(col[4]) if col[4] else ''}")
    except sqlite3.OperationalError as e:
        print(f"Error checking invoices table: {e}")
    
    # Check if we can query the invoices table
    try:
        cursor.execute("SELECT COUNT(*) FROM invoices")
        count = cursor.fetchone()[0]
        print(f"\nFound {count} invoices in the database")
    except sqlite3.OperationalError as e:
        print(f"\nError querying invoices: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_database_schema()
