import React, { useState } from "react";
import "./RegisterForm.css";
import { regions } from "../data/locationData"; // 지역 트리 import

function RegisterForm({ onSubmit, onCancel }) {
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    age: "",
    gender: "M",
    region1: "",
    region2: ""
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: value,
      ...(name === "region1" ? { region2: "" } : {}) // 상위 지역 바꾸면 하위 초기화
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const finalForm = {
      ...form,
      region: `${form.region1} ${form.region2}` // 백엔드에 넘길 실제 값
    };
    onSubmit(finalForm);
  };

  return (
    <div className="register-form">
      <h2>회원가입</h2>
      <form onSubmit={handleSubmit}>
        <input name="name" placeholder="이름" onChange={handleChange} required />
        <input name="email" type="email" placeholder="이메일" onChange={handleChange} required />
        <input name="password" type="password" placeholder="비밀번호" onChange={handleChange} required />
        <input name="age" type="number" placeholder="나이" onChange={handleChange} required />

        <select name="gender" onChange={handleChange} required>
          <option value="M">남성</option>
          <option value="F">여성</option>
        </select>

        {/* 시/도 선택 */}
        <label>시/도</label>
        <select name="region1" value={form.region1} onChange={handleChange} required>
          <option value="">시/도 선택</option>
          {Object.keys(regions).map((sido) => (
            <option key={sido} value={sido}>{sido}</option>
          ))}
        </select>

        {/* 시/군/구 선택 */}
        {form.region1 && (
          <>
            <label>시/군/구</label>
            <select name="region2" value={form.region2} onChange={handleChange} required>
              <option value="">시/군/구 선택</option>
              {regions[form.region1].map((sigungu) => (
                <option key={sigungu} value={sigungu}>{sigungu}</option>
              ))}
            </select>
          </>
        )}

        <button type="submit">가입하기</button>
        <button type="button" onClick={onCancel}>닫기</button>
      </form>
    </div>
  );
}

export default RegisterForm;
