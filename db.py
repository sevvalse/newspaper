import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except Exception as e:
        print(f"Veritabanına bağlanırken hata oluştu: {e}")
        return None

def create_tables():
    query = """
    CREATE TABLE IF NOT EXISTS news (
        id SERIAL PRIMARY KEY,
        source VARCHAR(100) NOT NULL,
        title TEXT NOT NULL,
        link TEXT UNIQUE NOT NULL,
        summary TEXT,
        raw_text TEXT,
        ai_analysis TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            cur.execute(query)
            conn.commit()
            print("PostgreSQL şeması başarıyla doğrulandı/oluşturuldu.")
    except Exception as e:
        print(f"Tablo oluşturulurken hata: {e}")
    finally:
        conn.close()

def clear_yesterdays_data():
    query = """
    DELETE FROM news 
    WHERE created_at < NOW() - INTERVAL '1 day';
    """
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            cur.execute(query)
            conn.commit()
            print("1 günden eski olan geçmiş haber verileri başarıyla temizlendi.")
    except Exception as e:
        print(f"Veri silme işlemi başarısız oldu: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_tables()