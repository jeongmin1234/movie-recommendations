from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

# MariaDB 연결 함수
def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='1234', 
        db='movie_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# 회원가입 API
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
                data['password'],
                data['region']
            ))
        conn.commit()
        conn.close()
        return jsonify({"message": "회원가입 성공!"}), 200
    except Exception as e:
        print("오류:", e)
        return jsonify({"error": "회원가입 실패"}), 500

# 로그인 API
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql, (data['email'],))
            user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({"error": "존재하지 않는 이메일입니다."}), 401
        if user['password'] != data['password']:
            return jsonify({"error": "비밀번호가 틀렸습니다."}), 401

        return jsonify({
            "id": user["id"],
            "name": user["name"],
            "region": user["region"]
        })

    except Exception as e:
        print("로그인 오류:", e)
        return jsonify({"error": "로그인 실패"}), 500

if __name__ == '__main__':
    app.run(debug=True)
