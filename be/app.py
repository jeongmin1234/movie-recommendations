from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import hashlib
import requests

app = Flask(__name__)
CORS(app)

# SHA256 암호화
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# DB 연결
def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='1234',
        db='movie_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# 회원가입
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            sql = "INSERT INTO users (name, email, password, region) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (
                data['name'],
                data['email'],
                hash_password(data['password']),
                data['region']
            ))
        conn.commit()
        conn.close()
        return jsonify({"message": "회원가입 성공"}), 200
    except Exception as e:
        print("회원가입 오류:", e)
        return jsonify({"error": "회원가입 실패"}), 500

# 로그인
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (data['email'],))
            user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({"error": "존재하지 않는 이메일입니다."}), 401
        if user['password'] != hash_password(data['password']):
            return jsonify({"error": "비밀번호가 틀렸습니다."}), 401

        return jsonify({
            "id": user["id"],
            "name": user["name"],
            "region": user["region"]
        }), 200

    except Exception as e:
        print("로그인 오류:", e)
        return jsonify({"error": "로그인 실패"}), 500

# 클릭 로그 저장
@app.route('/api/click-log', methods=['POST'])
def click_log():
    data = request.json
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            sql = "INSERT INTO click_logs (user_id, movie_id, genre) VALUES (%s, %s, %s)"
            cursor.execute(sql, (data['user_id'], data['movie_id'], data['genre']))
        conn.commit()
        conn.close()
        return jsonify({"message": "클릭 로그 저장 완료"}), 200
    except Exception as e:
        print("클릭 로그 오류:", e)
        return jsonify({"error": "로그 저장 실패"}), 500

# TMDB 영화 저장 (여러 페이지 저장 + GET/POST 허용)
@app.route('/api/fetch-tmdb', methods=['GET', 'POST'])
def fetch_tmdb_movies():
    print("✅ /api/fetch-tmdb 요청 수신됨")
    api_key = "9ff94e07935a34995a96b843e643a8a3"
    genre_url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}&language=ko-KR"
    genre_res = requests.get(genre_url)
    genre_data = genre_res.json().get("genres", [])
    genre_map = {g["id"]: g["name"] for g in genre_data}

    conn = get_connection()
    with conn.cursor() as cursor:
        for page in range(1, 11):
            url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}&language=ko-KR&page={page}"
            response = requests.get(url)
            movies = response.json().get("results", [])

            print(f"📦 Page {page} - 수신 영화 개수: {len(movies)}")

            for m in movies:
                try:
                    if not m.get('poster_path'):
                        print(f"❌ 포스터 없음: {m['title']}")
                        continue
                    poster_url = f"https://image.tmdb.org/t/p/w500{m['poster_path']}"
                    genre_names = [genre_map.get(gid, "") for gid in m.get("genre_ids", [])]
                    genre_str = ",".join(filter(None, genre_names))
                    sql = """
                    INSERT INTO movies (id, title, genre, region, poster_url)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        m["id"],
                        m["title"],
                        genre_str,
                        "",
                        poster_url
                    ))
                    print(f"✅ 저장 완료: {m['title']}")
                except Exception as e:
                    print(f"❌ 저장 실패: {m.get('title', 'Unknown')} - {e}")
    conn.commit()
    conn.close()
    return jsonify({"message": "TMDB 영화 저장 완료"})

# 무작위 영화 추천
@app.route('/api/movies/random', methods=['GET'])
def random_movies():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM movies ORDER BY RAND() LIMIT 10")
        movies = cursor.fetchall()
    conn.close()
    return jsonify(movies)

if __name__ == '__main__':
    app.run(debug=True)
