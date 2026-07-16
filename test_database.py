from database import get_connection


def show_last_token_logs(limit: int = 5):
    """
    PostgreSQL veritabanındaki son token kullanım kayıtlarını listeler.
    """

    query = """
    SELECT
        id,
        question,
        route,
        input_tokens,
        output_tokens,
        total_tokens,
        created_at
    FROM token_usage_logs
    ORDER BY id DESC
    LIMIT %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()

    if not rows:
        print("Henüz token kaydı bulunamadı.")
        return

    print("\nSon Token Kullanım Kayıtları")
    print("-" * 60)

    for row in rows:
        log_id, question, route, input_tokens, output_tokens, total_tokens, created_at = row

        print(f"ID: {log_id}")
        print(f"Soru: {question}")
        print(f"Route: {route}")
        print(f"Input Tokens: {input_tokens}")
        print(f"Output Tokens: {output_tokens}")
        print(f"Total Tokens: {total_tokens}")
        print(f"Tarih: {created_at}")
        print("-" * 60)


if __name__ == "__main__":
    show_last_token_logs()