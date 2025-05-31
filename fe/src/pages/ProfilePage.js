import React from "react";
import { useNavigate } from "react-router-dom";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from "chart.js";

// Chart.js 등록
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const ProfilePage = ({ user, recommendMovies }) => {
  const navigate = useNavigate();
  const comp = recommendMovies[0]?.components || {};

  return (
    <div className="profile-page" style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}>
      <h2>👤 사용자 프로필</h2>
      <p><strong>이름:</strong> {user?.name}</p>
      <p><strong>나이:</strong> {user?.age}</p>
      <p><strong>지역:</strong> {user?.region}</p>

      <h3 style={{ marginTop: "3rem" }}>🎬 추천 근거 TOP5 시각화</h3>
      <img
        src={`http://localhost:5000/api/user/stats/graph/${user?.id}`}
        alt="추천 근거 그래프"
        style={{
          width: "100%",
          border: "1px solid #ccc",
          borderRadius: "8px",
          marginTop: "1rem"
        }}
      />

      {/* 뒤로가기 버튼 */}
      <div style={{ marginTop: "2rem", textAlign: "center" }}>
        <button onClick={() => navigate("/")} style={{ padding: "0.5rem 1rem", fontSize: "16px" }}>
          ⬅ 추천 화면으로 돌아가기
        </button>
      </div>
    </div>
  );
};

export default ProfilePage;
