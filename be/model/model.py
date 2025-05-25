import torch
import torch.nn as nn

class MovieRecModel(nn.Module):
    def __init__(self, num_users, num_movies, num_regions, keyword_input_dim):
        super().__init__()
        self.user_embedding = nn.Embedding(num_users, 50)
        self.movie_embedding = nn.Embedding(num_movies, 50)
        self.region_embedding = nn.Embedding(num_regions, 5)
        self.keyword_fc = nn.Linear(keyword_input_dim, 32)

        self.fc1 = nn.Linear(50 + 50 + 5 + 32 + 1, 128)  # 1 = age
        self.fc2 = nn.Linear(128, 1)

    def forward(self, user_id, movie_id, region_id, keywords, age):
        u = self.user_embedding(user_id)
        m = self.movie_embedding(movie_id)
        r = self.region_embedding(region_id)
        k = torch.relu(self.keyword_fc(keywords))
        x = torch.cat([u, m, r, k, age.unsqueeze(1)], dim=1)
        x = torch.relu(self.fc1(x))
        return torch.sigmoid(self.fc2(x)).squeeze()
