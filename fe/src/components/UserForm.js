import React, { useState } from "react";

const UserForm = ({ onRecommend }) => {
  const [userId, setUserId] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onRecommend(userId);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="number"
        value={userId}
        onChange={(e) => setUserId(e.target.value)}
        placeholder="사용자 ID 입력"
      />
      <button type="submit">추천 받기</button>
    </form>
  );
};

export default UserForm;
