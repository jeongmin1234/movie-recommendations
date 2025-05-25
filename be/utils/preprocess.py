# be/utils/preprocess.py
import pandas as pd
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        db=os.getenv('DB_NAME'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def generate_dataset():
    os.makedirs("be/data", exist_ok=True)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    c.user_id, 
                    c.movie_id, 
                    u.age, 
                    u.region,
                    GROUP_CONCAT(DISTINCT s.keyword) AS keywords,
                    1 AS clicked
                FROM click_logs c
                JOIN users u ON u.id = c.user_id
                LEFT JOIN search_logs s ON s.user_id = c.user_id
                GROUP BY c.user_id, c.movie_id
            """)
            data = cursor.fetchall()

        df = pd.DataFrame(data)
        df['keywords'] = df['keywords'].fillna("")
        df.to_csv("../data/dataset.csv", index=False)
        print("✅ dataset.csv 저장 완료")
    finally:
        conn.close()
        
if __name__ == '__main__':
    generate_dataset()
