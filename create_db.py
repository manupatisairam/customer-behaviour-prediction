import MySQLdb
import os
import sys

def create_database():
    try:
        # Connect to MySQL server
        db = MySQLdb.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            user=os.environ.get("DB_USER", "root"),
            passwd=os.environ.get("DB_PASSWORD", ""),
        )
        cursor = db.cursor()
        
        # Create database
        database_name = os.environ.get("DB_NAME", "call_center_db")
        escaped_database_name = database_name.replace("`", "``")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{escaped_database_name}`")
        print("Database 'call_center_db' created or already exists.")
        
        db.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_database()
