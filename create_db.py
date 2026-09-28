import MySQLdb
import sys

def create_database():
    try:
        # Connect to MySQL server
        db = MySQLdb.connect(
            host="localhost",
            user="root",
            passwd="root"
        )
        cursor = db.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS call_center_db")
        print("Database 'call_center_db' created or already exists.")
        
        db.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_database()
