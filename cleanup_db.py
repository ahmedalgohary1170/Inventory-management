import os
import sqlite3

def cleanup_database():
    db_path = os.path.expanduser("~/Documents/.installments.db")
    print(f"Cleaning up database at: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("\nCurrent tables:", ", ".join(tables) if tables else "No tables found")
        
        # Drop any old/duplicate tables
        for table in ['invoices_old', 'invoices_new']:
            if table in tables:
                print(f"Dropping table: {table}")
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
        
        # Commit changes and close
        conn.commit()
        conn.close()
        
        print("\nDatabase cleanup complete. You can now restart the application.")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    cleanup_database()
