# normalize_perfumes.py (FIXED VERSION)

import csv  # Working with CSV files
import sqlite3  # Working with SQLite database
import os  # Working with filesystem

# --- Constants ---
DATA_DIR = 'data'  # Folder where CSV and database are located
CSV_FILE = os.path.join(DATA_DIR, 'perfumes_master.csv')  # Path to CSV file
DB_FILE = os.path.join(DATA_DIR, 'perfumes.db')  # Path to SQLite database

def setup_database(cursor):
    """Creates tables and indexes in the database."""
    # Table for original perfumes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OriginalPerfume (
        id TEXT PRIMARY KEY,  # Unique original ID
        brand TEXT,  # Original brand
        name TEXT,  # Original name
        price_eur REAL,  # Price in euros
        url TEXT  # Link to original
    )
    ''')
    
    # Table for perfume copies
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CopyPerfume (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  # Auto-increment copy ID
        original_id TEXT,  # Reference to original
        brand TEXT,  # Copy brand
        name TEXT,  # Copy name
        price_eur REAL,  # Copy price in euros
        url TEXT,  # Link to copy
        notes TEXT,  # Additional notes
        saved_amount REAL,  # Savings compared to original
        FOREIGN KEY (original_id) REFERENCES OriginalPerfume(id)  # Relation to original
    )
    ''')
    
    # Index to speed up searching copies by original
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_copy_original_id ON CopyPerfume(original_id)')
    print("Database structure successfully created.")

def clean_value(value):
    """Converts empty strings to None."""
    return None if not value or value.strip() == '' else value  # If empty string or None → None

def to_float(value):
    """Safely converts value to float, returns None on error."""
    if value is None:
        return None  # If no value, return None
    try:
        return float(value)  # Try to convert to float
    except (ValueError, TypeError):
        return None  # Return None if conversion fails

def process_data():
    """Main function to read CSV and write data into SQLite."""
    os.makedirs(DATA_DIR, exist_ok=True)  # Create data folder if missing
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)  # Delete old database if exists
        
    conn = sqlite3.connect(DB_FILE)  # Connect to database
    cursor = conn.cursor()  # Get cursor for executing SQL
    
    setup_database(cursor)  # Create tables and indexes
    
    # Dictionary to store already added original IDs
    # Key: (brand, name), Value: id
    original_id_map = {}
    
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8') as file:  # Open CSV
            reader = csv.DictReader(file)  # Read rows as dictionaries
            
            for row in reader:  # Iterate through each CSV row
                og_brand = clean_value(row.get('og_brand'))  # Clean original brand
                og_name = clean_value(row.get('og_name'))  # Clean original name
                
                if not og_brand or not og_name:
                    continue  # Skip rows without brand or name
                
                original_key = (og_brand, og_name)  # Key for original map
                
                # --- 1. Process original ---
                if original_key not in original_id_map:  # If original not added yet
                    original_id_for_db = clean_value(row.get('id'))  # Take original ID
                    
                    if not original_id_for_db:
                        continue  # Skip if no ID

                    original_data = (
                        original_id_for_db,  # ID
                        og_brand,  # Brand
                        og_name,  # Name
                        to_float(clean_value(row.get('og_price_eur'))),  # Price, float or None
                        clean_value(row.get('og_url'))  # URL
                    )
                    cursor.execute(
                        "INSERT INTO OriginalPerfume (id, brand, name, price_eur, url) VALUES (?, ?, ?, ?, ?)",
                        original_data  # Add original to DB
                    )
                    original_id_map[original_key] = original_id_for_db  # Save ID in map
                
                # --- 2. Process copy ---
                correct_original_id = original_id_map[original_key]  # Get correct original ID

                copy_data = (
                    correct_original_id,  # Original ID
                    clean_value(row.get('copy_brand')),  # Copy brand
                    clean_value(row.get('copy_name')),  # Copy name
                    to_float(clean_value(row.get('copy_price_eur'))),  # Copy price
                    clean_value(row.get('copy_url')),  # Copy URL
                    clean_value(row.get('notes')),  # Notes
                    to_float(clean_value(row.get('saved_amount')))  # Savings
                )
                cursor.execute(
                    """
                    INSERT INTO CopyPerfume 
                    (original_id, brand, name, price_eur, url, notes, saved_amount) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    copy_data  # Add copy to DB
                )

        conn.commit()  # Commit changes to database
        print(f"Data successfully imported. Added {len(original_id_map)} unique originals.")
        
    except FileNotFoundError:
        print(f"Error: file {CSV_FILE} not found.")  # If CSV missing
    except Exception as e:
        print(f"An error occurred: {e}")  # Catch other errors
        conn.rollback()  # Rollback transaction
    finally:
        conn.close()  # Close database connection

if __name__ == "__main__":
    process_data()  # Run data processing
