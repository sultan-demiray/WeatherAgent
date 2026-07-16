from dotenv import load_dotenv
import os
import json
import psycopg


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    """
    PostgreSQL veritabanına bağlantı oluşturur.
    """

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL .env dosyasında bulunamadı.")

    return psycopg.connect(DATABASE_URL)


def create_token_usage_table():
    """
    Token kullanım bilgilerini tutacak tabloyu oluşturur.
    Tablo zaten varsa tekrar oluşturmaz.
    """

    create_table_query = """
    CREATE TABLE IF NOT EXISTS token_usage_logs (
        id SERIAL PRIMARY KEY,
        question TEXT NOT NULL,
        route VARCHAR(50) NOT NULL,
        input_tokens INTEGER DEFAULT 0,
        output_tokens INTEGER DEFAULT 0,
        total_tokens INTEGER DEFAULT 0,
        usage_details JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(create_table_query)
            conn.commit()


def save_token_usage(question: str, route: str, token_usage: dict):
    """
    Kullanıcı sorusunu, route bilgisini ve token kullanımını veritabanına kaydeder.
    """

    insert_query = """
    INSERT INTO token_usage_logs (
        question,
        route,
        input_tokens,
        output_tokens,
        total_tokens,
        usage_details
    )
    VALUES (%s, %s, %s, %s, %s, %s);
    """

    input_tokens = token_usage.get("input_tokens", 0)
    output_tokens = token_usage.get("output_tokens", 0)
    total_tokens = token_usage.get("total_tokens", 0)
    usage_details = token_usage.get("details", {})

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                insert_query,
                (
                    question,
                    route,
                    input_tokens,
                    output_tokens,
                    total_tokens,
                    json.dumps(usage_details)
                )
            )
            conn.commit()