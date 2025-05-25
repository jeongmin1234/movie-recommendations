import React from 'react';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../components/LoginForm';
import SearchBar from '../components/SearchBar';
import LatestMovies from '../components/LatestMovies';

const LoginPage = ({ setUser }) => {
  const navigate = useNavigate();

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    navigate('/recommend'); // 로그인 성공하면 추천 페이지로 이동
  };

  const handleShowRegister = () => {
    navigate('/register'); // 회원가입 페이지로 이동
  };

  return (
    <>
      <SearchBar />
      <LatestMovies show={false} />
      <LoginForm onLogin={handleLoginSuccess} onShowRegister={handleShowRegister} />
    </>
  );
};

export default LoginPage;
