import React, { useState } from "react";
import "./RegisterForm.css";

const LoginForm = ({ onSubmit, onCancel }) => {
  const [form, setForm] = useState({
    email: "",
    password: ""
  });

  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await onSubmit(form);
    } catch (err) {
      setError(err.message || "로그인 실패");
    }
  };

  return (
    <form className="register-form" onSubmit={handleSubmit}>
      <h2>로그인</h2>
      {error && <div className="error-message">{error}</div>}
      <input
        name="email"
        type="email"
        placeholder="ID (이메일 형태로 입력)"
        onChange={handleChange}
        required
      />
      <input
        name="password"
        type="password"
        placeholder="비밀번호"
        onChange={handleChange}
        required
      />
      <div className="button-row">
        <button type="submit">로그인</button>
        <button type="button" onClick={onCancel}>닫기</button>
      </div>
    </form>
  );
};

export default LoginForm;
