const API_BASE_URL = 'http://localhost:8000/api/v1'

// Флаг для использования mock данных
const USE_MOCK_DATA = false;

// Mock данные для разработки
const MOCK_VACANCIES = [
  {
    vacancy_id: 1,
    title: 'Frontend Developer (Vue.js)',
    level: 'middle',
    description: 'Разработка пользовательских интерфейсов для HR-платформы',
    requirements: 'Опыт работы с Vue.js 2+ года, знание JavaScript, HTML5, CSS3',
    status: 'active',
    hr_id: 1,
    created_at: '2024-01-15T10:00:00'
  },
  {
    vacancy_id: 2,
    title: 'Backend Developer (Python)',
    level: 'senior',
    description: 'Разработка бэкенд-системы для HR-платформы',
    requirements: 'Опыт работы с Python 3+ года, FastAPI, PostgreSQL, Redis',
    status: 'active',
    hr_id: 1,
    created_at: '2024-01-16T14:30:00'
  }
];

export const api = {
  // ============ АУТЕНТИФИКАЦИЯ ============
  
  async registerUser(userData) {
    if (USE_MOCK_DATA) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            message: "User registered successfully",
            user_id: Math.floor(Math.random() * 1000),
            email: userData.email
          });
        }, 1000);
      });
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка регистрации');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  },

  async loginUser(credentials) {
    if (USE_MOCK_DATA) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            access_token: 'mock_access_token_' + Math.random().toString(36).substr(2),
            refresh_token: 'mock_refresh_token_' + Math.random().toString(36).substr(2),
            token_type: 'bearer'
          });
        }, 1000);
      });
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка входа');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  async refreshToken(refreshToken) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken })
      });
      
      if (!response.ok) {
        throw new Error('Token refresh failed');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Token refresh error:', error);
      throw error;
    }
  },

  async logoutUser(refreshToken) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken })
      });
      
      if (!response.ok) {
        console.warn('Logout request failed, but continuing...');
      }
      
      return { success: true };
    } catch (error) {
      console.error('Logout error:', error);
      return { success: false };
    }
  },

  // ============ ВАКАНСИИ ============

  async getMyVacancies() {
    if (USE_MOCK_DATA) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve(MOCK_VACANCIES);
        }, 1000);
      });
    }

    const tokens = authUtils.getTokens();
    const response = await fetch(`${API_BASE_URL}/vacancies/my`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${tokens.access_token}`,
        'Content-Type': 'application/json',
      }
    });
  
    if (!response.ok) {
      throw new Error(`Failed to fetch vacancies: ${response.status}`);
    }
  
    return await response.json();
  },

  async getAllVacancies(statusFilter = 'active') {
    if (USE_MOCK_DATA) {
      return new Promise((resolve) => {
        setTimeout(() => {
          const filtered = statusFilter 
            ? MOCK_VACANCIES.filter(v => v.status === statusFilter)
            : MOCK_VACANCIES;
          resolve(filtered);
        }, 1000);
      });
    }

    const url = statusFilter 
      ? `${API_BASE_URL}/vacancies?status_filter=${statusFilter}`
      : `${API_BASE_URL}/vacancies`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });
  
    if (!response.ok) {
      throw new Error(`Failed to fetch vacancies: ${response.status}`);
    }
  
    return await response.json();
  },

  async getVacancy(vacancyId) {
    if (USE_MOCK_DATA) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const vacancy = MOCK_VACANCIES.find(v => v.vacancy_id === vacancyId);
          if (vacancy) {
            resolve(vacancy);
          } else {
            reject(new Error('Vacancy not found'));
          }
        }, 1000);
      });
    }

    const response = await fetch(`${API_BASE_URL}/vacancies/${vacancyId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });
  
    if (!response.ok) {
      throw new Error(`Failed to fetch vacancy: ${response.status}`);
    }
  
    return await response.json();
  },

  async createVacancy(vacancyData) {
    if (USE_MOCK_DATA) {
      return new Promise((resolve) => {
        setTimeout(() => {
          const newVacancy = {
            vacancy_id: Date.now(),
            ...vacancyData,
            status: 'active',
            hr_id: 1,
            created_at: new Date().toISOString()
          };
          MOCK_VACANCIES.push(newVacancy);
          resolve(newVacancy);
        }, 1000);
      });
    }

    const tokens = authUtils.getTokens();
    const response = await fetch(`${API_BASE_URL}/vacancies/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${tokens.access_token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(vacancyData)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Failed to create vacancy: ${response.status}`);
    }
    
    return await response.json();
  },

  async updateVacancy(vacancyId, vacancyData) {
    if (USE_MOCK_DATA) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const index = MOCK_VACANCIES.findIndex(v => v.vacancy_id === vacancyId);
          if (index !== -1) {
            MOCK_VACANCIES[index] = { ...MOCK_VACANCIES[index], ...vacancyData };
            resolve(MOCK_VACANCIES[index]);
          } else {
            reject(new Error('Vacancy not found'));
          }
        }, 1000);
      });
    }

    const tokens = authUtils.getTokens();
    const response = await fetch(`${API_BASE_URL}/vacancies/${vacancyId}`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${tokens.access_token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(vacancyData)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Failed to update vacancy: ${response.status}`);
    }
    
    return await response.json();
  },

  async deleteVacancy(vacancyId) {
    if (USE_MOCK_DATA) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const index = MOCK_VACANCIES.findIndex(v => v.vacancy_id === vacancyId);
          if (index !== -1) {
            MOCK_VACANCIES[index].status = 'closed';
            resolve({ success: true });
          } else {
            reject(new Error('Vacancy not found'));
          }
        }, 1000);
      });
    }

    const tokens = authUtils.getTokens();
    const response = await fetch(`${API_BASE_URL}/vacancies/${vacancyId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${tokens.access_token}`,
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Failed to delete vacancy: ${response.status}`);
    }
    
    return { success: true };
  }
}

// Вспомогательные функции для работы с аутентификацией
export const authUtils = {
  // Сохранение токенов
  saveTokens(tokens) {
    if (tokens.access_token) {
      localStorage.setItem('access_token', tokens.access_token);
    }
    if (tokens.refresh_token) {
      localStorage.setItem('refresh_token', tokens.refresh_token);
    }
  },

  // Получение токенов
  getTokens() {
    return {
      access_token: localStorage.getItem('access_token'),
      refresh_token: localStorage.getItem('refresh_token')
    };
  },

  // Удаление токенов
  clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  // Проверка авторизации
  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  },

  // Получение заголовков с авторизацией
  getAuthHeaders() {
    const tokens = this.getTokens();
    return {
      'Authorization': `Bearer ${tokens.access_token}`,
      'Content-Type': 'application/json',
    };
  }
}
