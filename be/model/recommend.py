import torch
import pandas as pd
from train_model import MovieRecModel
from sklearn.preprocessing import LabelEncoder

# ✅ 추천 수행 함수
def load_and_recommend(user_row, model_path="be/model/model.pth", csv_path="be/data/dataset.csv"):
    df = pd.read_csv(csv_path)

    le_user = LabelEncoder().fit(df['user_id'])
    le_movie = LabelEncoder().fit(df['movie_id'])
    le_region = LabelEncoder().fit(df['region'])

    df['user_id'] = le_user.transform(df['user_id'])
    df['movie_id'] = le_movie.transform(df['movie_id'])
    df['region_id'] = le_region.transform(df['region'])

    # keyword 처리
    keyword_set = set()
    for kw in df['keywords']: keyword_set.update(kw.split(','))
    keyword_cols = []
    for k in sorted(keyword_set):
        col = f'kw_{k}'
        df[col] = df['keywords'].apply(lambda x: 1 if k in x else 0)
        keyword_cols.append(col)

    # 후보 영화 목록 준비
    movie_candidates = df[['movie_id'] + keyword_cols + ['title', 'genre', 'poster_url']].drop_duplicates('movie_id')

    model = MovieRecModel(len(le_user.classes_), len(le_movie.classes_), len(le_region.classes_), len(keyword_cols))
    model.load_state_dict(torch.load(model_path))
    model.eval()

    # 사용자 입력값 처리
    user_id = 0
    region_id = le_region.transform([user_row['region']])[0]
    age = torch.tensor([user_row['age']], dtype=torch.float32)
    
    keyword_vec = [1 if k in user_row['keywords'] else 0 for k in sorted(keyword_set)]
    keyword_tensor = torch.tensor([keyword_vec], dtype=torch.float32)

    results = []
    for _, row in movie_candidates.iterrows():
        movie_id = torch.tensor([row['movie_id']], dtype=torch.long)
        region = torch.tensor([region_id], dtype=torch.long)
        user = torch.tensor([user_id], dtype=torch.long)
        kw = keyword_tensor
        pred = model(user, movie_id, region, kw, age).item()
        results.append((row['title'], row['genre'], row['poster_url'], pred))

    sorted_res = sorted(results, key=lambda x: x[3], reverse=True)[:10]
    return [{"title": t, "genre": g, "poster_url": p, "score": round(s, 3)} for t, g, p, s in sorted_res]
