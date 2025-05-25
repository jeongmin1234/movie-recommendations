import React, { useState } from 'react';
import { register } from '../api/userApi';

const RegisterForm = ({ onBack }) => {
  const [form, setForm] = useState({ name: '', email: '', password: '', age: '', gender: 'M', region: '' });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await register(form);
    if (res.success) {
      alert('회원가입 성공');
      onBack();
    } else {
      alert('회원가입 실패');
    }
  };

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      <h3>회원가입</h3>
      <input name="name" placeholder="이름" onChange={handleChange} required style={styles.input} />
      <input name="email" type="email" placeholder="이메일" onChange={handleChange} required style={styles.input} />
      <input name="password" type="password" placeholder="비밀번호" onChange={handleChange} required style={styles.input} />
      <input name="age" type="number" placeholder="나이" onChange={handleChange} required style={styles.input} />
      <select name="gender" onChange={handleChange} required style={styles.input}>
        <option value="M">남성</option>
        <option value="F">여성</option>
      </select>
      <input name="region" placeholder="지역" onChange={handleChange} required style={styles.input} />
      <button
        type="submit"
        style={styles.button}
        onMouseOver={(e) => (e.target.style.transform = 'scale(1.05)')}
        onMouseOut={(e) => (e.target.style.transform = 'scale(1)')}
      >
        가입하기
      </button>
      <button type="button" onClick={onBack} style={{ ...styles.button, background: '#aaa' }}>뒤로</button>
    </form>
  );
};

const styles = {
  form: {
    display: 'flex', flexDirection: 'column', gap: '0.5rem', maxWidth: '300px',
    padding: '1rem', border: '1px solid #ccc', borderRadius: '8px', marginTop: '1rem', transition: '0.3s'
  },
  input: { padding: '0.5rem', fontSize: '1rem' },
  button: {
    padding: '0.5rem', background: '#555', color: '#fff', border: 'none', cursor: 'pointer', transition: 'transform 0.2s'
  }
};

export default RegisterForm;
