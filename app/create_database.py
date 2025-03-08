import psycopg2
from dotenv import load_dotenv
import os
import time

load_dotenv()

def create_database():
    retries = 5
    retry_count = 0
    
    while retry_count < retries:
        try:
            # Connect directly to the database
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Execute schema.sql
            with open('app/schema.sql') as f:
                schema = f.read()
            
            cursor.execute(schema)
            print("Tables created successfully!")
            
            cursor.close()
            conn.close()
            return True
            
        except psycopg2.OperationalError as e:
            print(f"Database connection failed (attempt {retry_count+1}/{retries}): {e}")
            retry_count += 1
            if retry_count < retries:
                print(f"Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("Failed to connect to the database after multiple retries.")
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            conn.rollback()  # Rollback any failed transaction
            retry_count += 1
            time.sleep(1)
            if retry_count >= retries:
                return False

if __name__ == "__main__":
    create_database()