from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import hashlib
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import torch
from model.train_model import MovieRecModel
import joblib

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})
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

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_info(user_id):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT age, region FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return None
        cursor.execute("SELECT keyword FROM search_logs WHERE user_id = %s", (user_id,))
        user['keywords'] = [row['keyword'] for row in cursor.fetchall()]
        cursor.execute("SELECT movie_id FROM click_logs WHERE user_id = %s", (user_id,))
        user['clicks'] = [row['movie_id'] for row in cursor.fetchall()]
    conn.close()
    return user

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            sql = "INSERT INTO users (name, email, password_hash, region, age) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (data['name'], data['email'], hash_password(data['password']), data['region'], data['age']))
        conn.commit()
        return jsonify({"message": "회원가입 성공"}), 200
    except Exception as e:
        return jsonify({"error": "회원가입 실패", "details": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (data['email'],))
            user = cursor.fetchone()
        if not user:
            return jsonify({"error": "존재하지 않는 이메일입니다."}), 401
        if user['password_hash'] != hash_password(data['password']):
            return jsonify({"error": "비밀번호가 틀렸습니다."}), 401
        return jsonify({"id": user["id"], "name": user["name"], "region": user["region"], "age": user["age"]}), 200
    except Exception as e:
        return jsonify({"error": "로그인 실패", "details": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/movies/latest', methods=['GET'])
def latest_movies():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, poster_url, genre, rating FROM movies ORDER BY id DESC LIMIT 20")
            return jsonify(cursor.fetchall())
    finally:
        conn.close()

@app.route('/api/movies/random', methods=['GET'])
def random_movies():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, poster_url, genre, rating FROM movies ORDER BY RAND() LIMIT 10")
            return jsonify(cursor.fetchall())
    finally:
        conn.close()

@app.route('/api/click-log', methods=['POST'])
def click_log():
    data = request.json
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT age, region FROM users WHERE id = %s", (data['user_id'],))
            user_info = cursor.fetchone()
            if not user_info:
                return jsonify({"error": "사용자 정보 없음"}), 400
            sql = "INSERT INTO click_logs (user_id, movie_id, genre, age, region) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (
                data['user_id'], data['movie_id'], data['genre'],
                user_info['age'], user_info['region']
            ))
        conn.commit()
        return jsonify({"message": "클릭 로그 저장 완료"}), 200
    except Exception as e:
        return jsonify({"error": "로그 저장 실패", "details": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/recommend/age/<int:user_id>', methods=['GET'])
def recommend_by_age(user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT age FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify([])
            cursor.execute("""
                SELECT movie_id FROM click_logs
                WHERE FLOOR(age / 10) = FLOOR(%s / 10)
                GROUP BY movie_id ORDER BY COUNT(*) DESC LIMIT 10
            """, (user['age'],))
            movie_ids = [row['movie_id'] for row in cursor.fetchall()]
            if not movie_ids:
                return jsonify([])
            format_str = ','.join(['%s'] * len(movie_ids))
            cursor.execute(f"""
                SELECT id, title, poster_url, genre, rating
                FROM movies WHERE id IN ({format_str})
            """, tuple(movie_ids))
            return jsonify(cursor.fetchall())
    except Exception as e:
        return jsonify({"error": "연령대 추천 실패", "details": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/recommend/region/<int:user_id>', methods=['GET'])
def recommend_by_region(user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT region FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify([])
            cursor.execute("""
                SELECT movie_id, COUNT(*) as cnt FROM click_logs c
                JOIN users u ON c.user_id = u.id
                WHERE u.region = %s
                GROUP BY movie_id ORDER BY cnt DESC LIMIT 10
            """, (user['region'],))
            movie_ids = [row['movie_id'] for row in cursor.fetchall()]
            if not movie_ids:
                return jsonify([])
            format_str = ','.join(['%s'] * len(movie_ids))
            cursor.execute(f"""
                SELECT id, title, poster_url, genre, rating
                FROM movies WHERE id IN ({format_str})
            """, tuple(movie_ids))
            return jsonify(cursor.fetchall())
    except Exception as e:
        return jsonify({"error": "지역 추천 실패", "details": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/recommend/preference/<user_id>', methods=['GET'])
def recommend_by_preference(user_id):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT genre, COUNT(*) as cnt FROM click_logs
                WHERE user_id = %s GROUP BY genre ORDER BY cnt DESC LIMIT 1
            """, (user_id,))
            top = cursor.fetchone()
            if not top:
                return jsonify([])
            cursor.execute("""
                SELECT id, title, genre, poster_url, rating FROM movies
                WHERE genre LIKE %s ORDER BY rating DESC LIMIT 10
            """, (f"%{top['genre']}%",))
            return jsonify(cursor.fetchall())
    except Exception as e:
        return jsonify({"error": "장르 기반 추천 실패", "details": str(e)}), 500

@app.route('/api/movies/search', methods=['GET'])
def search_movies():
    query = request.args.get('query', '').strip()
    user_id = request.args.get('user_id')
    if not query:
        return jsonify({"result": [], "related": []})

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            if user_id:
                cursor.execute("SELECT age, region FROM users WHERE id = %s", (user_id,))
                user_info = cursor.fetchone()
                if user_info:
                    cursor.execute("""
                        INSERT INTO search_logs (user_id, keyword, age, region)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, query, user_info['age'], user_info['region']))

            cursor.execute("SELECT id, title, poster_url, genre FROM movies WHERE title LIKE %s LIMIT 1", (f"%{query}%",))
            movie = cursor.fetchone()
            if not movie:
                return jsonify({"result": [], "related": []})

            genre_keywords = set(movie['genre'].split(','))
            cursor.execute("SELECT id, title, poster_url, genre FROM movies WHERE id != %s", (movie['id'],))
            candidates = cursor.fetchall()
            scored = []
            for m in candidates:
                genres = set(m['genre'].split(','))
                score = len(genre_keywords.intersection(genres))
                if score > 0:
                    scored.append((score, m))

            scored.sort(reverse=True, key=lambda x: x[0])
            top_related = [m for _, m in scored[:10]]
            return jsonify({"result": movie, "related": top_related})
    except Exception as e:
        return jsonify({"error": "검색 실패", "details": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/recommend/hybrid/<int:user_id>', methods=['GET'])
def hybrid_recommendation(user_id):
    try:
        def safe_transform(le, val, default=0):
            return le.transform([val])[0] if val in le.classes_ else default

        user = get_user_info(user_id)
        if not user:
            return jsonify([])

        df = pd.read_csv("data/dataset.csv")
        df['user_id'] = df['user_id'].astype(int)
        df['movie_id'] = df['movie_id'].astype(int)

        le_user = joblib.load("model/le_user.pkl")
        le_movie = joblib.load("model/le_movie.pkl")
        le_region = joblib.load("model/le_region.pkl")
        vectorizer = joblib.load("model/vectorizer.pkl")

        # ✅ Encoding with fallback
        df['user_id_enc'] = df['user_id'].apply(lambda x: safe_transform(le_user, x, default=0))
        df['movie_id_enc'] = df['movie_id'].apply(lambda x: safe_transform(le_movie, x, default=0))
        df['region_enc'] = df['region'].apply(lambda x: safe_transform(le_region, x, default=0))

        user_enc = safe_transform(le_user, int(user_id), default=0)
        region_enc = safe_transform(le_region, user['region'], default=0)
        age = torch.tensor([user['age']], dtype=torch.float32)

        keyword_matrix = vectorizer.transform(df['keywords'].fillna(""))
        keyword_tensor = torch.tensor(keyword_matrix.toarray(), dtype=torch.float32)

        model = MovieRecModel(
            num_users=len(le_user.classes_),
            num_movies=len(le_movie.classes_),
            num_regions=len(le_region.classes_),
            keyword_dim=keyword_tensor.shape[1]
        )
        model.load_state_dict(torch.load("model/model.pth", map_location='cpu'))
        model.eval()

        movies = df[['movie_id', 'movie_id_enc']].drop_duplicates()

        input_data = []
        for _, row in movies.iterrows():
            movie_id, movie_enc = row['movie_id'], row['movie_id_enc']
            keywords = keyword_tensor[df['movie_id'] == movie_id].mean(dim=0)
            input_data.append((
                torch.tensor([user_enc]),
                torch.tensor([movie_enc]),
                torch.tensor([region_enc]),
                keywords.unsqueeze(0),
                age
            ))

        results = []
        for user_t, movie_t, region_t, keyword_t, age_t in input_data:
            with torch.no_grad():
                score = model(user_t, movie_t, region_t, keyword_t, age_t).item()
            results.append((le_movie.inverse_transform([movie_t.item()])[0], score))

        results.sort(key=lambda x: x[1], reverse=True)
        top_ids = [movie_id for movie_id, _ in results[:10]]

        conn = get_connection()
        with conn.cursor() as cursor:
            format_str = ','.join(['%s'] * len(top_ids))
            cursor.execute(f"""
                SELECT id, title, poster_url, genre, rating
                FROM movies
                WHERE id IN ({format_str})
            """, tuple(top_ids))
            movie_data = cursor.fetchall()
        conn.close()

        return jsonify(movie_data)

    except Exception as e:
        print("🔥 Hybrid Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)