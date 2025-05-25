import os
import sys
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import joblib

# ✅ 시작 표시
print("✅ recommend.py 시작됨", flush=True)

# 현재 파일 경로를 sys.path에 추가 (train_model.py를 import하기 위함)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from train_model import MovieRecModel  # 같은 폴더 내 import

def main():
    print("📌 main() 진입", flush=True)

    df_path = "../data/dataset.csv"
    if not os.path.exists(df_path):
        print(f"❌ 파일 없음: {df_path}", flush=True)
        return

    df = pd.read_csv(df_path)
    print(f"✅ 데이터 로드 완료: {df.shape}", flush=True)

    # LabelEncoder 재학습
    le_user = LabelEncoder()
    le_user.fit(df['user_id'].astype(int))
    joblib.dump(le_user, "le_user.pkl")

    le_movie = LabelEncoder()
    le_movie.fit(df['movie_id'].astype(int))
    joblib.dump(le_movie, "le_movie.pkl")

    le_region = LabelEncoder()
    le_region.fit(df['region'].astype(str))
    joblib.dump(le_region, "le_region.pkl")

    print("✅ LabelEncoder 재학습 완료 및 저장됨", flush=True)

if __name__ == "__main__":
    print("🔥 if __name__ == '__main__' 조건 실행됨", flush=True)
    main()
