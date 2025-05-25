import React from 'react';
import { useNavigate } from 'react-router-dom';
import RegisterForm from '../components/RegisterForm';

const RegisterPage = () => {
  const navigate = useNavigate();

  const handleBackToLogin = () => {
    navigate('/login'); // 뒤로가기하면 로그인 페이지로
  };

  return (
    <RegisterForm onBack={handleBackToLogin} />
  );
};

export default RegisterPage;
