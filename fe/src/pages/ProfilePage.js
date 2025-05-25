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

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const ProfilePage = ({ user, recommendMovies }) => {
  const navigate = useNavigate();
  const comp = recommendMovies[0]?.components || {};

  return (
    <div className="profile-page" style={{ padding: "2rem", maxWidth: "700px", margin: "0 auto" }}>
      <h2>👤 사용자 프로필</h2>
      <p><strong>이름:</strong> {user?.name}</p>
      <p><strong>나이:</strong> {user?.age}</p>
      <p><strong>지역:</strong> {user?.region}</p>

      <h3>📊 추천 점수 구성 요소</h3>
      <Bar
        data={{
          labels: ["클릭", "지역", "연령", "TF-IDF"],
          datasets: [{
            label: "추천 점수",
            data: [
              comp.click_score ?? 0,
              comp.region_score ?? 0,
              comp.age_score ?? 0,
              comp.tfidf_score ?? 0
            ],
            backgroundColor: ["#42a5f5", "#66bb6a", "#ffa726", "#ab47bc"]
          }]
        }}
        options={{
          indexAxis: "y",
          scales: {
            x: { min: 0, max: 1, title: { display: true, text: "점수 (0 ~ 1)" } }
          },
          plugins: { legend: { display: false } }
        }}
      />

      {/* 뒤로가기 버튼 */}
      <div style={{ marginTop: "2rem", textAlign: "center" }}>
        <button onClick={() => navigate("/")} style={{ padding: "0.5rem 1rem" }}>
          ⬅ 추천 화면으로 돌아가기
        </button>
      </div>
    </div>
  );
};

export default ProfilePage;
