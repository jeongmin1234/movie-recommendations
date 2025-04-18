import React, { useState } from "react";
import RegisterForm from "./components/RegisterForm";
import LoginForm from "./components/LoginForm";
import axios from "axios";
import "./App.css";

function App() {
  const [user, setUser] = useState(null);
  const [showRegister, setShowRegister] = useState(false);
  const [showLogin, setShowLogin] = useState(false);

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
      throw new Error(message);
    }
  };

  const handleLogout = () => {
    setUser(null);
    setShowRegister(false);
    setShowLogin(false);
  };

  return (
    <div className="App">
      <h1>🎬 영화 추천 서비스</h1>

      {!user ? (
        <>
          {!showRegister && !showLogin && (
            <>
              <div className="image-container">
                <img src="/1.jpg" alt="포스터1" />
                <img src="/2.jpg" alt="포스터2" />
                <img src="/3.jpg" alt="포스터3" />
              </div>
              <button onClick={() => setShowLogin(true)}>로그인</button>
              <button onClick={() => setShowRegister(true)}>회원가입</button>
            </>
          )}
          {showRegister && (
            <RegisterForm
              onSubmit={handleRegister}
              onCancel={() => setShowRegister(false)}
            />
          )}
          {showLogin && (
            <LoginForm
              onSubmit={handleLogin}
              onCancel={() => setShowLogin(false)}
            />
          )}
        </>
      ) : (
        <>
          <h2>{user.name}님의 추천 영화</h2>

          {/* ✅ 로그인 후 이미지 출력 */}
          <div className="image-container">
            <img src="/3.jpg" alt="추천영화2" />
            <img src="/4.jpg" alt="추천영화4" />
            <img src="/5.jpg" alt="추천영화5" />
          </div>

          <button onClick={handleLogout}>로그아웃</button>
        </>
      )}
    </div>
  );
}

export default App;
