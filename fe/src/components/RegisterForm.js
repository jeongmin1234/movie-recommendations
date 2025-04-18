import React, { useState } from "react";
import "./RegisterForm.css";

const RegisterForm = ({ onSubmit, onCancel }) => {
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    region: ""
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(form);
  };

  return (
    <form className="register-form" onSubmit={handleSubmit}>
      <h2>회원가입</h2>
      <input name="name" placeholder="이름" onChange={handleChange} required />
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
      <input
        name="region"
        placeholder="지역"
        onChange={handleChange}
        required
      />
      <div className="button-row">
        <button type="submit">가입하기</button>
        <button type="button" onClick={onCancel}>닫기</button>
      </div>
    </form>
  );
};

export default RegisterForm;
