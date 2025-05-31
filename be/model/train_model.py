import os
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
import joblib

# ✅ Pickle 오류 방지를 위해 tokenizer 함수는 함수 바깥에 정의
def custom_tokenizer(text):
    return text.split(',')

class MovieDataset(Dataset):
    def __init__(self, df, keyword_cols):
        self.user = torch.tensor(df['user_id'].values, dtype=torch.long)
        self.movie = torch.tensor(df['movie_id'].values, dtype=torch.long)
        self.age = torch.tensor(df['age'].values, dtype=torch.float32)
        self.region = torch.tensor(df['region_id'].values, dtype=torch.long)
        self.keywords = torch.tensor(df[keyword_cols].values, dtype=torch.float32)
        self.label = torch.tensor(df['clicked'].values, dtype=torch.float32)

    def __len__(self): return len(self.user)

    def __getitem__(self, idx):
        return self.user[idx], self.movie[idx], self.region[idx], self.keywords[idx], self.age[idx], self.label[idx]

class MovieRecModel(nn.Module):
    def __init__(self, num_users, num_movies, num_regions, keyword_dim):
        super().__init__()
        self.user_embedding = nn.Embedding(num_users, 32)
        self.movie_embedding = nn.Embedding(num_movies, 32)
        self.region_embedding = nn.Embedding(num_regions, 8)
        self.keyword_fc = nn.Linear(keyword_dim, 16)
        self.fc = nn.Sequential(
            nn.Linear(32 + 32 + 8 + 16 + 1, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )

    def forward(self, user, movie, region, keywords, age):
        u = self.user_embedding(user)
        m = self.movie_embedding(movie)
        r = self.region_embedding(region)
        k = torch.relu(self.keyword_fc(keywords))
        x = torch.cat([u, m, r, k, age.unsqueeze(1)], dim=1)
        return torch.sigmoid(self.fc(x)).squeeze(-1)

def train():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "..", "data", "dataset.csv")
    df = pd.read_csv(csv_path)

    df = df[df['clicked'].isin([0, 1])]
    df['clicked'] = df['clicked'].astype(float)
    df = df[df['age'].notnull()]
    df['age'] = df['age'].astype(float)
    df['region'] = df['region'].fillna("기타")
    df['keywords'] = df['keywords'].fillna("")

    le_user = LabelEncoder()
    le_movie = LabelEncoder()
    le_region = LabelEncoder()
    df['user_id'] = le_user.fit_transform(df['user_id'])
    df['movie_id'] = le_movie.fit_transform(df['movie_id'])
    df['region_id'] = le_region.fit_transform(df['region'])

    # ✅ CountVectorizer로 키워드 벡터화
    cv = CountVectorizer(binary=True, token_pattern=r'[^,]+')
    keyword_matrix = cv.fit_transform(df['keywords'])
    keyword_df = pd.DataFrame(keyword_matrix.toarray(), columns=[f'kw_{t}' for t in cv.get_feature_names_out()])
    df = pd.concat([df.reset_index(drop=True), keyword_df.reset_index(drop=True)], axis=1)
    keyword_cols = keyword_df.columns.tolist()

    df['keyword_sum'] = df[keyword_cols].sum(axis=1)
    df = df[df['keyword_sum'] > 0]

    dataset = MovieDataset(df, keyword_cols)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)

    model = MovieRecModel(
        num_users=len(le_user.classes_),
        num_movies=len(le_movie.classes_),
        num_regions=len(le_region.classes_),
        keyword_dim=len(keyword_cols)
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0005)
    loss_fn = nn.BCEWithLogitsLoss()

    for epoch in range(5):
        for user, movie, region, keywords, age, label in loader:
            pred = model(user, movie, region, keywords, age)
            loss = loss_fn(pred, label.squeeze())
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        print(f"Epoch {epoch+1}: Loss={loss.item():.4f}")

    model_dir = os.path.join(BASE_DIR, "..", "model")
    os.makedirs(model_dir, exist_ok=True)
    torch.save(model.state_dict(), os.path.join(model_dir, "model.pth"))
    joblib.dump(le_user, os.path.join(model_dir, "le_user.pkl"))
    joblib.dump(le_movie, os.path.join(model_dir, "le_movie.pkl"))
    joblib.dump(le_region, os.path.join(model_dir, "le_region.pkl"))
    joblib.dump(cv, os.path.join(model_dir, "vectorizer.pkl"))  # ✅ 저장 가능

if __name__ == "__main__":
    train()
