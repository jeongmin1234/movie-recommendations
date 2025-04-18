from db.database import get_connection

def get_movies_by_region_genre(region, genre):
    conn = get_connection()
    with conn.cursor() as cursor:
        sql = "SELECT * FROM movies WHERE region=%s AND genre=%s"
        cursor.execute(sql, (region, genre))
        result = cursor.fetchall()
    conn.close()
    return result
