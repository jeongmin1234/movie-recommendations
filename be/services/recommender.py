from models.user_model import get_user_by_id
from models.movie_model import get_movies_by_region_genre

def recommend_movies(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return []
    region = user['region']
    genre = user['genre']
    return get_movies_by_region_genre(region, genre)
