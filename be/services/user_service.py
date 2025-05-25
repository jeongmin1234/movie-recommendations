import hashlib
from db.connection import get_connection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(data):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            print("📥 받은 데이터:", data)  # 입력 확인용 로그
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, age, gender, region)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                data['name'],
                data['email'],
                hash_password(data['password']),
                int(data['age']),             # ⚠️ age가 문자열일 경우 int로 변환
                data['gender'],
                data['region']
            ))
        conn.commit()
        print("✅ 회원가입 성공")
        return True
    except Exception as e:
        print("❌ 회원가입 실패:", e)
        return False
    finally:
        conn.close()

def login_user(email, password):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user and user['password_hash'] == hash_password(password):
                return user
            return None
    finally:
        conn.close()
