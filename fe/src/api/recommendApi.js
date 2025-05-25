import axios from 'axios';

export const fetchRecommendations = async (userId) => {
    const res = await axios.get(`/api/recommend/${userId}`);
    return res.data;
};
