import React, { useState, useEffect } from "react";
import RegisterForm from "./components/RegisterForm";
import LoginForm from "./components/LoginForm";
import axios from "axios";
import "./App.css";

function App() {
  const [user, setUser] = useState(null);
  const [showRegister, setShowRegister] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [movies, setMovies] = useState([]);

  const handleRegister = async (form) => {
    try {
      await axios.post("http://localhost:5000/api/register", form);
      alert("회원가입이 완료되었습니다. 로그인해주세요.");
      setShowRegister(false);
      setShowLogin(true);
    } catch (err) {
      alert("회원가입 실패");
      console.error(err);
    }
  };

  const handleLogin = async (form) => {
    try {
      const res = await axios.post("http://localhost:5000/api/login", form);
      setUser(res.data);
      setShowLogin(false);
    } catch (err) {
      const message = err.response?.data?.error || "로그인 실패";
      alert(message);
    }
  };

  const handlePosterClick = (movieId, genre) => {
    if (!user) return;
    axios.post("http://localhost:5000/api/click-log", {
      user_id: user.id,
      movie_id: movieId,
      genre: genre
    }).then(() => {
      console.log(`✅ 클릭 로그 저장됨: 영화 ID ${movieId}, 장르 ${genre}`);
    }).catch(err => {
      console.error("❌ 클릭 로그 저장 실패", err);
    });
  };

  const handleLogout = () => {
    setUser(null);
    setShowRegister(false);
    setShowLogin(false);
    setMovies([]);
  };

  useEffect(() => {
    axios.get("http://localhost:5000/api/movies/random")
      .then((res) => setMovies(res.data))
      .catch((err) => console.error("영화 로딩 실패", err));
  }, []);

  return (
    <div className="App">
      <h1>🎬 영화 추천 서비스</h1>

      {!user ? (
        <>
          {!showRegister && !showLogin && (
            <>
              <div className="image-container">
                {movies.map((movie) => (
                  <div key={movie.id}>
                    <img
                      src={movie.poster_url}
                      alt={movie.title}
                      style={{ width: '150px', height: '220px', objectFit: 'cover' }}
                    />
                    <p>{movie.title}</p>
                  </div>
                ))}
              </div>
              <button onClick={() => setShowLogin(true)}>로그인</button>
              <button onClick={() => setShowRegister(true)}>회원가입</button>
            </>
          )}
          {showRegister && (
            <RegisterForm onSubmit={handleRegister} onCancel={() => setShowRegister(false)} />
          )}
          {showLogin && (
            <LoginForm onSubmit={handleLogin} onCancel={() => setShowLogin(false)} />
          )}
        </>
      ) : (
        <>
          <h2>{user.name}님의 추천 영화</h2>

          <div className="image-container">
            {movies.map((movie) => (
              <div key={movie.id}>
                <img
                  src={movie.poster_url}
                  alt={movie.title}
                  style={{ width: '150px', height: '220px', objectFit: 'cover' }}
                  onClick={() => handlePosterClick(movie.id, movie.genre)}
                />
                <p>{movie.title}</p>
              </div>
            ))}
          </div>

          <button onClick={handleLogout}>로그아웃</button>
        </>
      )}
    </div>
  );
}

export default App;
