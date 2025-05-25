import requests
import pymysql

# TMDB API KEY
TMDB_API_KEY = '9ff94e07935a34995a96b843e643a8a3'

# DB 연결 함수
def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='1234',
        db='movie_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# 장르 매핑
GENRE_MAP = {
    28: "액션", 12: "모험", 16: "애니메이션", 35: "코미디",
    80: "범죄", 18: "드라마", 10751: "가족", 14: "판타지",
    36: "역사", 27: "공포", 10402: "음악", 9648: "미스터리",
    10749: "로맨스", 878: "SF", 10770: "TV 영화", 53: "스릴러",
    10752: "전쟁", 37: "서부극"
}

def fetch_and_store_movies(max_pages=20):  # 최대 400개
    url = 'https://api.themoviedb.org/3/movie/popular'
    conn = get_connection()
    inserted = 0
    try:
        with conn.cursor() as cursor:
            for page in range(1, max_pages + 1):
                params = {
                    'api_key': TMDB_API_KEY,
                    'language': 'ko-KR',
                    'page': page
                }
                response = requests.get(url, params=params)
                if response.status_code != 200:
                    print(f"❌ page {page} 불러오기 실패:", response.status_code)
                    break

                data = response.json()
                movies = data.get('results', [])
                if not movies:
                    print(f"✅ page {page} 더 이상 영화 없음")
                    break

                for movie in movies:
                    try:
                        genre_names = [GENRE_MAP.get(gid, str(gid)) for gid in movie.get('genre_ids', [])]
                        genre_str = ','.join(genre_names)

                        # 삽입만 하고, 이미 존재하는 영화는 무시 (UPDATE 안 함)
                        cursor.execute("""
                            INSERT IGNORE INTO movies (id, title, genre, rating, poster_url, release_date)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            movie['id'],
                            movie['title'],
                            genre_str,
                            movie['vote_average'],
                            f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get('poster_path') else None,
                            movie.get('release_date')
                        ))
                        inserted += cursor.rowcount
                    except Exception as e:
                        print(f"❌ 삽입 실패: {movie.get('title')} / 오류: {e}")
                conn.commit()
                print(f"✅ page {page} 완료 (누적 {inserted}개 삽입됨)")
    finally:
        conn.close()

# 실행
if __name__ == '__main__':
    fetch_and_store_movies()
