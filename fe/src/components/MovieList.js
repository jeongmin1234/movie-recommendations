import React from "react";

const MovieList = ({ movies }) => {
  return (
    <div>
      <h2>추천 영화</h2>
      <ul>
        {movies.map((movie) => (
          <li key={movie.id}>{movie.title} ({movie.genre}, {movie.region})</li>
        ))}
      </ul>
    </div>
  );
};

export default MovieList;
