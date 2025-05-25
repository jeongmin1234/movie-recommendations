import axios from 'axios';

export const register = async (userData) => {
    const res = await axios.post('/api/register', userData);
    return res.data;
};

export const login = async (email, password) => {
    const res = await axios.post('/api/login', { email, password });

    // 서버에서 받은 데이터가 어떤지 파악하고
    // 명시적으로 success, user로 만들어주기
    const data = res.data;

    if (data && data.id && data.name && data.email) {
        // 사용자 정보가 바로 오는 경우 (success 없이)
        return {
            success: true,
            user: {
                id: data.id,
                name: data.name,
                email: data.email
            }
        };
    } else if (data && data.success && data.user) {
        // 정상적으로 success, user 형태로 오는 경우
        return {
            success: data.success,
            user: data.user
        };
    } else {
        // 그 외 모든 실패 케이스
        return { success: false };
    }
};
