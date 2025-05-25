import React, { useState, useEffect } from "react";
import RegisterForm from "./components/RegisterForm";
import LoginForm from "./components/LoginForm";
import MovieModal from "./components/MovieModal";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import axios from "axios";
import ProfilePage from "./pages/ProfilePage";
import "./App.css";

function App() {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem("user");
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [showRegister, setShowRegister] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [latestMovies, setLatestMovies] = useState([]);
  const [recommendMovies, setRecommendMovies] = useState([]);
  const [regionalMovies, setRegionalMovies] = useState([]);
  const [ageGroupMovies, setAgeGroupMovies] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [searchVisible, setSearchVisible] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResult, setSearchResult] = useState(null);
  const [relatedMovies, setRelatedMovies] = useState([]);
  const [activeFilter, setActiveFilter] = useState("all");

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
      localStorage.setItem("user", JSON.stringify(res.data));
      setShowLogin(false);
    } catch (err) {
      const message = err.response?.data?.error || "로그인 실패";
      alert(message);
    }
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem("user");
    setRecommendMovies([]);
    setLatestMovies([]);
    setRegionalMovies([]);
    setAgeGroupMovies([]);
    setActiveFilter("all");
    setSearchResult(null);
    setRelatedMovies([]);
  };

  const loadMovies = async () => {
    try {
      if (user) {
        const [latest, hybrid, regional, age] = await Promise.all([
          axios.get("http://localhost:5000/api/movies/latest"),
          axios.get(`http://localhost:5000/api/recommend/hybrid/${user.id}`),
          axios.get(`http://localhost:5000/api/recommend/region/${user.id}`),
          axios.get(`http://localhost:5000/api/recommend/age/${user.id}`)
        ]);
        setLatestMovies(latest.data);
        setRecommendMovies(hybrid.data);
        setRegionalMovies(regional.data);
        setAgeGroupMovies(age.data);
      } else {
        const randomRes = await axios.get("http://localhost:5000/api/movies/random");
        setLatestMovies(randomRes.data);
      }
    } catch (err) {
      console.error("영화 불러오기 실패", err);
    }
  };

  useEffect(() => {
    loadMovies();
  }, [user]);

  const handlePosterClick = (movie) => {
    if (user) {
      axios.post("http://localhost:5000/api/click-log", {
        user_id: user.id,
        movie_id: movie.id,
        genre: movie.genre || "",
        age: user.age,
        region: user.region
      }).then(() => {
        console.log("✅ 클릭 로그 저장 완료");
      }).catch((err) => {
        console.error("❌ 클릭 로그 저장 실패", err);
      });
    }

    setSelectedMovie({
      ...movie,
      rating: movie.rating ?? "정보 없음",
      genre: movie.genre ?? "장르 정보 없음"
    });
  };

  const handleSearch = async () => {
    if (!searchQuery || !user) return;
    try {
      const res = await axios.get(`http://localhost:5000/api/movies/search?query=${searchQuery}&user_id=${user.id}`);
      setSearchResult(res.data.result);
      setRelatedMovies(res.data.related);
    } catch (err) {
      console.error("❌ 검색 오류", err);
    }
  };

  return (
    <Router>
      <div className="App">
        <div className="top-bar">
          <div className="top-bar-left">
            <Link to="/" style={{ textDecoration: "none", color: "inherit" }}>
              DEEP MOVIE
            </Link>
          </div>
          <div className="top-bar-right">
            <button className="search-icon" onClick={() => setSearchVisible(!searchVisible)}>🔍</button>
            {user && <Link to="/profile"><button>👤 프로필</button></Link>}
            {!user ? (
              <button className="login-button" onClick={() => { setShowLogin(true); setShowRegister(false); }}>
                로그인
              </button>
            ) : (
              <button className="logout-button black" onClick={handleLogout}>
                로그아웃
              </button>
            )}
          </div>
        </div>

        <Routes>
          <Route path="/profile" element={
            <ProfilePage
              user={user}
              recommendMovies={recommendMovies}
              onBack={() => window.history.back()}
            />
          } />

          <Route path="/" element={
            <>
              {searchVisible && user && (
                <form onSubmit={(e) => { e.preventDefault(); handleSearch(); }} className="search-form">
                  <input
                    type="text"
                    placeholder="영화 검색..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  <button type="submit">검색</button>
                  <button type="button" onClick={() => {
                    setSearchResult(null);
                    setSearchQuery("");
                    setRelatedMovies([]);
                  }}>⬅️ 뒤로가기</button>
                </form>
              )}

              {showLogin && (
                <LoginForm
                  onSubmit={handleLogin}
                  onCancel={() => setShowLogin(false)}
                  showRegisterLink={() => {
                    setShowLogin(false);
                    setShowRegister(true);
                  }}
                />
              )}

              {showRegister && (
                <RegisterForm
                  onSubmit={handleRegister}
                  onCancel={() => setShowRegister(false)}
                />
              )}

              {searchResult && (
                <>
                  <h2>🔍 검색 결과</h2>
                  <div className="search-result">
                    <img src={searchResult.poster_url} alt={searchResult.title} onClick={() => handlePosterClick(searchResult)} />
                    <p>{searchResult.title}</p>
                  </div>

                  <h3>📎 관련 영화</h3>
                  <div className="scroll-container">
                    {relatedMovies.map((movie) => (
                      <div key={movie.id} onClick={() => handlePosterClick(movie)}>
                        <img src={movie.poster_url} alt={movie.title} />
                        <p>{movie.title}</p>
                      </div>
                    ))}
                  </div>
                </>
              )}

              {user && !searchResult && (
                <>
                  <div className="filter-buttons">
                    <button onClick={() => setActiveFilter("recommend")}>추천</button>
                    <button onClick={() => setActiveFilter("region")}>지역기반</button>
                    <button onClick={() => setActiveFilter("age")}>연령대기반</button>
                    <button onClick={() => setActiveFilter("latest")}>최신</button>
                    <button onClick={() => setActiveFilter("all")}>전체</button>
                  </div>

                  {(activeFilter === "recommend" || activeFilter === "all") && (
                    <>
                      <h2>🎯 추천 영화</h2>
                      <div className="scroll-container">
                        {recommendMovies.map((movie) => (
                          <div key={movie.id}>
                            <img src={movie.poster_url} alt={movie.title} onClick={() => handlePosterClick(movie)} />
                            <p>{movie.title}</p>
                          </div>
                        ))}
                      </div>
                    </>
                  )}

                  {(activeFilter === "region" || activeFilter === "all") && (
                    <>
                      <h2>📍 지역 기반 영화</h2>
                      <div className="scroll-container">
                        {regionalMovies.length > 0 ? (
                          regionalMovies.map((movie) => (
                            <div key={movie.id}>
                              <img src={movie.poster_url} alt={movie.title} onClick={() => handlePosterClick(movie)} />
                              <p>{movie.title}</p>
                            </div>
                          ))
                        ) : (
                          <p>해당 지역의 추천 영화가 없습니다.</p>
                        )}
                      </div>
                    </>
                  )}

                  {(activeFilter === "age" || activeFilter === "all") && (
                    <>
                      <h2>👤 연령대 기반 영화</h2>
                      <div className="scroll-container">
                        {ageGroupMovies.length > 0 ? (
                          ageGroupMovies.map((movie) => (
                            <div key={movie.id}>
                              <img src={movie.poster_url} alt={movie.title} onClick={() => handlePosterClick(movie)} />
                              <p>{movie.title}</p>
                            </div>
                          ))
                        ) : (
                          <p>해당 연령대의 추천 영화가 없습니다.</p>
                        )}
                      </div>
                    </>
                  )}

                  {(activeFilter === "latest" || activeFilter === "all") && (
                    <>
                      <h2>🆕 최신 영화</h2>
                      <div className="scroll-container">
                        {latestMovies.map((movie) => (
                          <div key={movie.id}>
                            <img src={movie.poster_url} alt={movie.title} onClick={() => handlePosterClick(movie)} />
                            <p>{movie.title}</p>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </>
              )}

              {!user && !showLogin && !showRegister && (
                <>
                  <h2>🎬 다양한 영화 둘러보기</h2>
                  <div className="centered-movie-container">
                    {latestMovies.map((movie) => (
                      <div key={movie.id} onClick={() => setSelectedMovie(movie)}>
                        <img src={movie.poster_url} alt={movie.title} />
                        <p>{movie.title}</p>
                      </div>
                    ))}
                  </div>
                </>
              )}

              {selectedMovie && (
                <MovieModal movie={selectedMovie} onClose={() => setSelectedMovie(null)} />
              )}
            </>
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
