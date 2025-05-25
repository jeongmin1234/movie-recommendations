from flask import Flask, jsonify
from collections import defaultdict
from db.connection import get_connection

app = Flask(__name__)

@app.route('/api/recommend/hybrid/<int:user_id>', methods=['GET'])
def hybrid_recommendation(user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT age, region FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify([])

            age, region = user['age'], user['region']
            score = defaultdict(float)

            # 사용자 클릭 로그 기반 (50%)
            cursor.execute("""
                SELECT movie_id, COUNT(*) as cnt FROM click_logs
                WHERE user_id = %s
                GROUP BY movie_id ORDER BY cnt DESC LIMIT 10
            """, (user_id,))
            clicked_movies = cursor.fetchall()
            clicked_ids = [row['movie_id'] for row in clicked_movies]
            for row in clicked_movies:
                score[row['movie_id']] += 0.5

            # 클릭한 영화들의 장르 수집
            genre_keywords = set()
            if clicked_ids:
                format_str = ','.join(['%s'] * len(clicked_ids))
                cursor.execute(f"SELECT genre FROM movies WHERE id IN ({format_str})", tuple(clicked_ids))
                for row in cursor.fetchall():
                    genres = row['genre'].split(',')
                    genre_keywords.update([g.strip() for g in genres])

            # 비슷한 장르 영화 점수 추가 (30%) - 텍스트 기반 매칭
            for genre in genre_keywords:
                cursor.execute("""
                    SELECT id FROM movies
                    WHERE genre LIKE %s
                    LIMIT 30
                """, (f"%{genre}%",))
                for row in cursor.fetchall():
                    score[row['id']] += 0.3

            # 지역 기반 (10%)
            cursor.execute("""
                SELECT movie_id FROM click_logs c
                JOIN users u ON c.user_id = u.id
                WHERE u.region = %s
                GROUP BY movie_id ORDER BY COUNT(*) DESC LIMIT 10
            """, (region,))
            for row in cursor.fetchall():
                score[row['movie_id']] += 0.1

            # 연령대 기반 (10%)
            cursor.execute("""
                SELECT movie_id FROM click_logs c
                JOIN users u ON c.user_id = u.id
                WHERE FLOOR(u.age / 10) = FLOOR(%s / 10)
                GROUP BY movie_id ORDER BY COUNT(*) DESC LIMIT 10
            """, (age,))
            for row in cursor.fetchall():
                score[row['movie_id']] += 0.1

            # 평점 기반 (10%)
            cursor.execute("""
                SELECT movie_id FROM ratings
                GROUP BY movie_id ORDER BY AVG(rating) DESC LIMIT 10
            """)
            for row in cursor.fetchall():
                score[row['movie_id']] += 0.1

            # 정렬 및 상위 추천 영화 추출
            top_movies = sorted(score.items(), key=lambda x: x[1], reverse=True)
            movie_ids = [m[0] for m in top_movies]
            movie_ids = list(dict.fromkeys(movie_ids))[:10]

            recommended_movies = []
            if movie_ids:
                format_str = ','.join(['%s'] * len(movie_ids))
                cursor.execute(f"SELECT id, title, genre, poster_url, rating FROM movies WHERE id IN ({format_str})", tuple(movie_ids))
                recommended_movies = cursor.fetchall()

            # 부족할 경우 평점 기반 보완 추천
            if len(recommended_movies) < 10:
                already_ids = tuple([m['id'] for m in recommended_movies])
                placeholders = ','.join(['%s'] * len(already_ids)) if already_ids else 'NULL'
                needed = 10 - len(recommended_movies)

                cursor.execute(f"""
                    SELECT id, title, genre, poster_url, rating FROM movies
                    WHERE id NOT IN ({placeholders})
                    ORDER BY rating DESC LIMIT %s
                """, (*already_ids, needed) if already_ids else (needed,))
                recommended_movies += cursor.fetchall()

            return jsonify(recommended_movies)

    except Exception as e:
        print("추천 오류:", e)
        return jsonify({"error": "추천 실패", "details": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)