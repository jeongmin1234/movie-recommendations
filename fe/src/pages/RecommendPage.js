import React from 'react';
import RecommendList from '../components/RecommendList';
import LatestMovies from '../components/LatestMovies';

const RecommendPage = ({ user, setUser }) => {
  const handleLogout = () => {
    setUser(null);
  };

  return (
    <>
      <h2 style={{ marginBottom: '1rem' }}>🎥 {user.name}님을 위한 추천 영화</h2>
      <button onClick={handleLogout} style={styles.logoutButton}>로그아웃</button>
      <RecommendList userId={user.id} />
      <LatestMovies show={true} />
    </>
  );
};

const styles = {
  logoutButton: {
    marginBottom: '1rem',
    padding: '0.5rem 1rem',
    backgroundColor: '#ff5555',
    color: '#fff',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '1rem'
  }
};

export default RecommendPage;
