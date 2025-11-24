const API_BASE_URL = 'http://localhost:8000'

// Флаг для использования mock данных
const USE_MOCK_DATA = false;

export const api = {
  // Регистрация пользователя (работодателя)
  async registerUser(userData) {
    if (USE_MOCK_DATA) {
      // Mock успешной регистрации
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
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
      })
      
      if (!response.ok) {
        let errorDetail = 'Ошибка регистрации'
        try {
          const errorData = await response.json()
          errorDetail = errorData.detail || errorData.message || errorDetail
        } catch (e) {
          errorDetail = await response.text()
        }
        
        throw new Error(`HTTP error! status: ${response.status}, details: ${errorDetail}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Registration error:', error)
      
      if (error.message.includes('Email already registered')) {
        throw new Error('Пользователь с таким email уже зарегистрирован')
      } else if (error.message.includes('Network Error') || error.message.includes('Failed to fetch')) {
        throw new Error('Не удалось подключиться к серверу. Проверьте, запущен ли бэкенд.')
      } else {
        throw new Error(error.message || 'Произошла ошибка при регистрации')
      }
    }
  },

  // Вход пользователя
  async loginUser(credentials) {
    if (USE_MOCK_DATA) {
      // Mock успешного входа
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            access_token: 'mock_access_token_' + Math.random().toString(36).substr(2),
            refresh_token: 'mock_refresh_token_' + Math.random().toString(36).substr(2)
          });
        }, 1000);
      });
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials)
      })
      
      if (!response.ok) {
        let errorDetail = 'Ошибка входа'
        try {
          const errorData = await response.json()
          errorDetail = errorData.detail || errorData.message || errorDetail
        } catch (e) {
          errorDetail = await response.text()
        }
        
        throw new Error(`HTTP error! status: ${response.status}, details: ${errorDetail}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Login error:', error)
      
      if (error.message.includes('Invalid email or password')) {
        throw new Error('Неверный email или пароль')
      } else if (error.message.includes('User account is blocked')) {
        throw new Error('Аккаунт заблокирован')
      } else if (error.message.includes('Network Error') || error.message.includes('Failed to fetch')) {
        throw new Error('Не удалось подключиться к серверу. Проверьте, запущен ли бэкенд.')
      } else {
        throw new Error(error.message || 'Произошла ошибка при входе')
      }
    }
  },

  // Обновление токена
  async refreshToken(refreshToken) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken })
      })
      
      if (!response.ok) {
        throw new Error(`Token refresh failed with status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Token refresh error:', error)
      throw new Error('Не удалось обновить токен')
    }
  },

  // Выход пользователя
  async logoutUser(refreshToken) {
      try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
          method: 'POST',
          headers: {
          'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh_token: refreshToken })
      })
      
      if (!response.ok) {
          console.warn('Logout request failed, but continuing...')
      }
      
      return { success: true }
      } catch (error) {
      console.error('Logout error:', error)
      // Не бросаем ошибку при логауте, так как это не критично
      return { success: false }
      }
  },

      // ========== ВАКАНСИИ ==========

  // Получить все вакансии пользователя
  async getMyVacancies() {
    if (USE_MOCK_DATA) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve([
            {
              id: 1,
              title: 'Frontend Developer (Vue.js)',
              level: 'middle',
              description: 'Разработка пользовательских интерфейсов для HR-платформы',
              requirements: 'Опыт работы с Vue.js 2+ года, знание JavaScript, HTML5, CSS3',
              status: 'active',
              created_at: '2024-01-15'
            },
            {
              id: 2,
              title: 'Backend Developer (Python)',
              level: 'senior',
              description: 'Разработка API и бизнес-логики платформы',
              requirements: 'Python 3+, FastAPI, PostgreSQL, опыт работы 3+ года',
              status: 'active',
              created_at: '2024-01-10'
            }
          ]);
        }, 1000);
      });
    }

    try {
      const tokens = authUtils.getTokens();
      const response = await fetch(`${API_BASE_URL}/api/v1/vacancies/my`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${tokens.access_token}`,
          'Content-Type': 'application/json',
        }
      });
    
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `HTTP error! status: ${response.status}`);
      }
    
      return await response.json();
    } catch (error) {
      console.error('Error fetching vacancies:', error);
      throw error;
    }
  },

  // Создать вакансию
  async createVacancy(vacancyData) {
    if (USE_MOCK_DATA) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            id: Date.now(),
            ...vacancyData,
            status: 'active',
            created_at: new Date().toISOString()
          });
        }, 1000);
      });
    }

    try {
      const tokens = authUtils.getTokens();
      const response = await fetch(`${API_BASE_URL}/api/v1/vacancies/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${tokens.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(vacancyData)
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error creating vacancy:', error);
      throw error;
    }
  },

  // Обновить вакансию
  async updateVacancy(vacancyId, vacancyData) {
    if (USE_MOCK_DATA) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            id: vacancyId,
            ...vacancyData,
            status: 'active',
            updated_at: new Date().toISOString()
          });
        }, 1000);
      });
    }

    try {
      const tokens = authUtils.getTokens();
      const response = await fetch(`${API_BASE_URL}/api/v1/vacancies/${vacancyId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${tokens.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(vacancyData)
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error updating vacancy:', error);
      throw error;
    }
  },

  // Удалить вакансию
  async deleteVacancy(vacancyId) {
    if (USE_MOCK_DATA) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({ success: true, message: 'Vacancy deleted successfully' });
        }, 1000);
      });
    }

    try {
      const tokens = authUtils.getTokens();
      const response = await fetch(`${API_BASE_URL}/api/v1/vacancies/${vacancyId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${tokens.access_token}`,
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `HTTP error! status: ${response.status}`);
      }
      
      // Для DELETE запроса с 204 No Content
      if (response.status === 204) {
        return { success: true, message: 'Vacancy deleted successfully' };
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error deleting vacancy:', error);
      throw error;
    }
  },


  // // Обновить вакансию
  // async updateVacancy(vacancyId, vacancyData) {
  //   if (USE_MOCK_DATA) {
  //     return new Promise((resolve) => {
  //       setTimeout(() => {
  //         resolve({
  //           id: vacancyId,
  //           ...vacancyData,
  //           status: 'active',
  //           updated_at: new Date().toISOString()
  //         });
  //       }, 1000);
  //     });
  //   }

  //   try {
  //     const tokens = authUtils.getTokens();
  //     const response = await fetch(`${API_BASE_URL}/api/v1/vacancies/${vacancyId}`, {
  //       method: 'PATCH',
  //       headers: {
  //         'Authorization': `Bearer ${tokens.access_token}`,
  //         'Content-Type': 'application/json',
  //       },
  //       body: JSON.stringify(vacancyData)
  //     });
      
  //     if (!response.ok) {
  //       const errorData = await response.json().catch(() => null);
  //       throw new Error(errorData?.detail || `HTTP error! status: ${response.status}`);
  //     }
      
  //     return await response.json();
  //   } catch (error) {
  //     console.error('Error updating vacancy:', error);
  //     throw error;
  //   }
  // },

  // // Удалить вакансию
  // async deleteVacancy(vacancyId) {
  //   if (USE_MOCK_DATA) {
  //     return new Promise((resolve) => {
  //       setTimeout(() => {
  //         resolve({ success: true, message: 'Vacancy deleted successfully' });
  //       }, 1000);
  //     });
  //   }

  //   try {
  //     const tokens = authUtils.getTokens();
  //     const response = await fetch(`${API_BASE_URL}/api/v1/vacancies/${vacancyId}`, {
  //       method: 'DELETE',
  //       headers: {
  //         'Authorization': `Bearer ${tokens.access_token}`,
  //       }
  //     });
      
  //     if (!response.ok) {
  //       const errorData = await response.json().catch(() => null);
  //       throw new Error(errorData?.detail || `HTTP error! status: ${response.status}`);
  //     }
      
  //     // Для DELETE запроса может не быть тела ответа
  //     if (response.status === 204) {
  //       return { success: true, message: 'Vacancy deleted successfully' };
  //     }
      
  //     return await response.json();
  //   } catch (error) {
  //     console.error('Error deleting vacancy:', error);
  //     throw error;
  //   }
  // },

  // Получить вакансию по ID
  // Получить кандидатов по вакансии
async getCandidatesByVacancy(vacancyId, filters = {}) {
  if (USE_MOCK_DATA) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          {
            candidate_id: 1,
            user_id: 1,
            name: 'Иван Петров',
            email: 'ivan.petrov@example.com',
            phone: '+7 (999) 123-45-67',
            resume_text: 'Frontend разработчик с опытом работы 3 года. Vue.js, JavaScript, HTML, CSS.',
            resume_file: '/uploads/resumes/1_cv.pdf',
            vacancy_id: vacancyId,
            status: 'new',
            created_at: new Date().toISOString()
          },
          {
            candidate_id: 2,
            user_id: 2,
            name: 'Мария Сидорова',
            email: 'maria.sidorova@example.com',
            phone: '+7 (999) 765-43-21',
            resume_text: 'Fullstack разработчик. Vue.js, Node.js, PostgreSQL.',
            resume_file: '/uploads/resumes/2_cv.pdf',
            vacancy_id: vacancyId,
            status: 'reviewed',
            created_at: new Date(Date.now() - 86400000).toISOString()
          }
        ]);
      }, 1000);
    });
  }

  try {
    const tokens = authUtils.getTokens();
    const params = new URLSearchParams();
    
    if (filters.status) params.append('status_filter', filters.status);
    if (filters.search) params.append('search', filters.search);
    
    const url = `${API_BASE_URL}/api/v1/candidates/vacancy/${vacancyId}?${params.toString()}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${tokens.access_token}`,
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching candidates:', error);
    throw error;
  }
  }, 

  // Получить детальную информацию о кандидате
async getCandidateDetails(candidateId, vacancyId = null) {
  if (USE_MOCK_DATA) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          candidate_id: candidateId,
          user_id: candidateId,
          name: 'Иван Петров',
          email: 'ivan.petrov@example.com',
          phone: '+7 (999) 123-45-67',
          resume_text: 'Frontend разработчик с опытом работы 3 года. Vue.js, JavaScript, HTML, CSS.',
          resume_file: '/uploads/resumes/1_cv.pdf',
          vacancy_id: vacancyId,
          status: 'new',
          created_at: new Date().toISOString(),
          parsed_text: 'Frontend разработчик с опытом работы 3 года. Vue.js, JavaScript, HTML, CSS.',
          metadata_json: {
            experience: '3 года',
            skills: ['Vue.js', 'JavaScript', 'HTML', 'CSS'],
            education: 'Высшее техническое'
          },
          upload_date: new Date().toISOString()
        });
      }, 1000);
    });
  }

  try {
    const tokens = authUtils.getTokens();
    const params = new URLSearchParams();
    
    if (vacancyId) params.append('vacancy_id', vacancyId);
    
    const url = `${API_BASE_URL}/api/v1/candidates/${candidateId}?${params.toString()}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${tokens.access_token}`,
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching candidate details:', error);
    throw error;
  }
},

// Обновить статус кандидата
async updateCandidateStatus(candidateId, vacancyId, status) {
  if (USE_MOCK_DATA) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          candidate_id: candidateId,
          user_id: candidateId,
          name: 'Иван Петров',
          email: 'ivan.petrov@example.com',
          phone: '+7 (999) 123-45-67',
          resume_text: 'Frontend разработчик с опытом работы 3 года. Vue.js, JavaScript, HTML, CSS.',
          resume_file: '/uploads/resumes/1_cv.pdf',
          vacancy_id: vacancyId,
          status: status,
          created_at: new Date().toISOString()
        });
      }, 1000);
    });
  }

  try {
    const tokens = authUtils.getTokens();
    const url = `${API_BASE_URL}/api/v1/candidates/${candidateId}/status?vacancy_id=${vacancyId}`;
    
    const response = await fetch(url, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${tokens.access_token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status })
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error updating candidate status:', error);
    throw error;
  }
},

// Получить всех кандидатов работодателя
async getAllCandidates(filters = {}) {
  if (USE_MOCK_DATA) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          {
            candidate_id: 1,
            user_id: 1,
            name: 'Иван Петров',
            email: 'ivan.petrov@example.com',
            phone: '+7 (999) 123-45-67',
            resume_text: 'Frontend разработчик с опытом работы 3 года. Vue.js, JavaScript, HTML, CSS.',
            resume_file: '/uploads/resumes/1_cv.pdf',
            vacancy_id: 1,
            status: 'new',
            created_at: new Date().toISOString()
          },
          {
            candidate_id: 2,
            user_id: 2,
            name: 'Мария Сидорова',
            email: 'maria.sidorova@example.com',
            phone: '+7 (999) 765-43-21',
            resume_text: 'Fullstack разработчик. Vue.js, Node.js, PostgreSQL.',
            resume_file: '/uploads/resumes/2_cv.pdf',
            vacancy_id: 2,
            status: 'reviewed',
            created_at: new Date(Date.now() - 86400000).toISOString()
          }
        ]);
      }, 1000);
    });
  }

  try {
    const tokens = authUtils.getTokens();
    const params = new URLSearchParams();
    
    if (filters.status) params.append('status_filter', filters.status);
    if (filters.search) params.append('search', filters.search);
    
    const url = `${API_BASE_URL}/api/v1/candidates?${params.toString()}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${tokens.access_token}`,
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching all candidates:', error);
    throw error;
  }
  }
}