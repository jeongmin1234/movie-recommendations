from db.database import get_connection

def get_user_by_id(user_id):
    conn = get_connection()
    with conn.cursor() as cursor:
        sql = "SELECT * FROM users WHERE id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
    conn.close()
    return result
