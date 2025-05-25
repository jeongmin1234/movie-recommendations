import React, { useState } from "react";

function LoginForm({ onSubmit, onCancel, showRegisterLink }) {
  const [form, setForm] = useState({ email: "", password: "" });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(form);
  };

  return (
    <form onSubmit={handleSubmit} className="auth-form">
      <h2>로그인</h2>
      <input
        type="email"
        name="email"
        placeholder="이메일"
        value={form.email}
        onChange={handleChange}
        required
      />
      <input
        type="password"
        name="password"
        placeholder="비밀번호"
        value={form.password}
        onChange={handleChange}
        required
      />
      <div>
        <button type="submit">로그인</button>
        <button type="button" onClick={onCancel}>취소</button>
      </div>
      <p>
        아직 회원이 아니신가요?{" "}
        <span style={{ color: "blue", cursor: "pointer" }} onClick={showRegisterLink}>
          회원가입
        </span>
      </p>
    </form>
  );
}

export default LoginForm;
