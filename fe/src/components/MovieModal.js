import React from "react";
import "./MovieModal.css";

function MovieModal({ movie, onClose }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <img
          src={movie.poster_url}
          alt={movie.title}
          className="modal-poster"
        />
        <h2>{movie.title}</h2>
        <p><strong>장르:</strong> {movie.genre || "장르 정보 없음"}</p>
        <p><strong>평점:</strong> {movie.rating || "정보 없음"}</p>
        <p><strong>추천 점수:</strong> {movie.score ? `${(movie.score * 100).toFixed(1)}%` : "정보 없음"}</p>
        <button className="modal-close" onClick={onClose}>닫기</button>
      </div>
    </div >
  );
}

export default MovieModal;
