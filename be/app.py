from flask import Flask, request, jsonify, send_file
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
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib import font_manager

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
        
        os.system("python model/train_model.py")
        
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
        return jsonify([])

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 🔹 사용자 정보 조회 및 검색 로그 저장
            if user_id:
                try:
                    cursor.execute("SELECT age, region FROM users WHERE id = %s", (user_id,))
                    user_info = cursor.fetchone()
                    if user_info:
                        cursor.execute("""
                            INSERT INTO search_logs (user_id, keyword, age, region)
                            VALUES (%s, %s, %s, %s)
                        """, (user_id, query, user_info['age'], user_info['region']))
                        conn.commit()
                        os.system("python model/train_model.py")
                    else:
                        print(f"❌ user_id {user_id} 없음, 검색 로그 저장 안 됨")
                except Exception as e:
                    print("🔥 검색 로그 저장 실패:", e)
            else:
                return jsonify([])

            # 🔹 영화 검색
            cursor.execute("SELECT id, title, poster_url, genre, rating FROM movies WHERE title LIKE %s LIMIT 1", (f"%{query}%",))
            movie = cursor.fetchone()
            if not movie:
                return jsonify([])

            # 🔹 후보 영화 조회
            cursor.execute("SELECT id, title, poster_url, genre, rating FROM movies WHERE id != %s", (movie['id'],))
            candidates = cursor.fetchall()

        # 🔹 모델 및 인코더 로드
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(BASE_DIR, "model", "model.pth")
        le_user = joblib.load(os.path.join(BASE_DIR, "model", "le_user.pkl"))
        le_movie = joblib.load(os.path.join(BASE_DIR, "model", "le_movie.pkl"))
        le_region = joblib.load(os.path.join(BASE_DIR, "model", "le_region.pkl"))
        vectorizer = joblib.load(os.path.join(BASE_DIR, "model", "vectorizer.pkl"))

        # 🔹 안전 인코딩 함수
        def safe_transform(le, val, default=0):
            return le.transform([val])[0] if val in le.classes_ else default

        user_enc = safe_transform(le_user, int(user_id))
        region_enc = safe_transform(le_region, user_info['region'])
        age = torch.tensor([user_info['age']], dtype=torch.float32)

        all_movies = [movie] + candidates
        texts = [m['genre'] for m in all_movies]
        keyword_matrix = vectorizer.transform(texts)
        keyword_tensor = torch.tensor(keyword_matrix.toarray(), dtype=torch.float32)

        model = MovieRecModel(
            num_users=len(le_user.classes_),
            num_movies=len(le_movie.classes_),
            num_regions=len(le_region.classes_),
            keyword_dim=keyword_tensor.shape[1]
        )
        model.load_state_dict(torch.load(model_path, map_location='cpu', weights_only=True))
        model.eval()

        results = []
        for i, m in enumerate(all_movies):
            movie_enc = safe_transform(le_movie, m['id'])
            with torch.no_grad():
                score = model(
                    torch.tensor([user_enc]),
                    torch.tensor([movie_enc]),
                    torch.tensor([region_enc]),
                    keyword_tensor[i].unsqueeze(0),
                    age
                ).item()
            m['score'] = round(score, 4)
            results.append(m)

        # 🔹 정렬 및 출력
        movie_result = results[0]
        related = sorted(results[1:], key=lambda x: x['score'], reverse=True)[:10]

        return jsonify([movie_result] + related)

    except Exception as e:
        print("🔥 Search Error:", e)
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

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(BASE_DIR, "model", "model.pth")
        le_user = joblib.load(os.path.join(BASE_DIR, "model", "le_user.pkl"))
        le_movie = joblib.load(os.path.join(BASE_DIR, "model", "le_movie.pkl"))
        le_region = joblib.load(os.path.join(BASE_DIR, "model", "le_region.pkl"))
        vectorizer = joblib.load(os.path.join(BASE_DIR, "model", "vectorizer.pkl"))

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
        model.load_state_dict(torch.load(model_path, map_location='cpu', weights_only=True))
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
        
        score_dict = {movie_id: round(score, 4) for movie_id, score in results[:10]}
        
        final_result = []
        for movie in movie_data:
            movie['score'] = score_dict.get(movie['id'], None)
            final_result.append(movie)
            
        return jsonify(final_result)

    except Exception as e:
        print("🔥 Hybrid Error:", e)
        return jsonify({"error": str(e)}), 500
@app.route('/api/user/stats/graph/<int:user_id>')
def user_profile_graph(user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT age, region FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({"error": "사용자 정보 없음"}), 404
            age = user['age']
            region = user['region']

            cursor.execute("""
                SELECT m.title, COUNT(*) as cnt FROM click_logs c
                JOIN movies m ON c.movie_id = m.id
                WHERE c.region = %s
                GROUP BY c.movie_id ORDER BY cnt DESC LIMIT 5
            """, (region,))
            region_rows = cursor.fetchall()

            cursor.execute("""
                SELECT m.title, COUNT(*) as cnt FROM click_logs c
                JOIN movies m ON c.movie_id = m.id
                WHERE c.age = %s
                GROUP BY c.movie_id ORDER BY cnt DESC LIMIT 5
            """, (age,))
            age_rows = cursor.fetchall()
            
            # 30대 전체 기준: 총 클릭 수 기준 인기 영화
            age_group = age // 10  # 파이썬에서 30대면 3으로 변환
            cursor.execute("""
                SELECT m.title, COUNT(*) AS total_clicks
                FROM click_logs c
                JOIN users u ON c.user_id = u.id
                JOIN movies m ON c.movie_id = m.id
                WHERE FLOOR(u.age / 10) = %s
                GROUP BY c.movie_id
                ORDER BY total_clicks DESC
                LIMIT 5;
            """, (age_group,))
            age_group_rows = cursor.fetchall()


            cursor.execute("""
                SELECT m.title, COUNT(*) as cnt FROM click_logs c
                JOIN movies m ON c.movie_id = m.id
                WHERE c.user_id = %s
                GROUP BY c.movie_id ORDER BY cnt DESC LIMIT 5
            """, (user_id,))
            user_rows = cursor.fetchall()

            # ✅ 한글 폰트 설정 (Windows용: 맑은 고딕)
            font_path = "C:/Windows/Fonts/malgun.ttf"
            font_name = font_manager.FontProperties(fname=font_path).get_name()
            plt.rc("font", family=font_name)
            plt.rcParams["axes.unicode_minus"] = False  # 마이너스 깨짐 방지

            # ✅ 깔끔한 스타일 설정
            plt.style.use("ggplot")
            fig, axes = plt.subplots(1, 4, figsize=(18, 5))
            fig.suptitle("사용자 영화 클릭 통계", fontsize=16, fontweight='bold')

            def plot_bar(ax, data, title, count_key='cnt'):
                if data:
                    titles = [row['title'] for row in data]
                    counts = [row[count_key] for row in data]
                    bars = ax.barh(titles[::-1], counts[::-1], color="#4B8BBE")

                    ax.set_title(title, fontsize=13, fontweight='bold')
                    ax.set_xlabel('클릭 수', fontsize=10)
                    ax.tick_params(axis='y', labelsize=9)
                    ax.grid(False)

                    # 막대 끝 클릭 수 표시
                    for bar in bars:
                        width = bar.get_width()
                        ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                                f"{int(width)}", va='center', fontsize=9)
                else:
                    ax.set_title(f"{title}\n(데이터 없음)", fontsize=11)
                    ax.axis('off')

            plot_bar(axes[0], region_rows, f"📍 {region} 지역 TOP 5")
            plot_bar(axes[1], age_rows, f"🎂 {age}세 연령 TOP 5")
            plot_bar(axes[2], age_group_rows, f"👥 {age_group * 10}대 인기 TOP 5", count_key='total_clicks')
            plot_bar(axes[3], user_rows, "🙋 내가 클릭한 TOP 5")

            fig.tight_layout(rect=[0, 0, 1, 0.93])  # 제목 공간 확보
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close(fig)
            return send_file(buf, mimetype='image/png')

    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)