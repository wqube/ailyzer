// !!! ВАЖНАЯ НАСТРОЙКА: БАЗОВЫЙ URL API !!!

// Определяем базовый URL в зависимости от среды:
// 1. Если это локальная разработка (например, localhost), используем локальный бэкенд.
// 2. Если это продакшн, используем публичный домен API.

let BASE_API_URL;

// Проверяем, запущен ли фронтенд локально (можно также проверить process.env.NODE_ENV === 'development')
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    // Используем локальный адрес бэкенда для разработки
    BASE_API_URL = 'http://localhost:8000';
} else {
    // !!! ЗАМЕНИТЕ ЭТОТ АДРЕС НА ВАШ ПРОДАКШН-ДОМЕН API !!!
    // Например: https://api.ailyzer.ru
    BASE_API_URL = 'https://employer.ailyzer.ru';
    // Запрос пойдет на: https://employer.ailyzer.ru/api/v1/auth/login
    // Caddy отправит на бэкенд: /v1/auth/login
}

// Флаг для использования mock данных (ставьте true только для тестов без бэкенда)
const USE_MOCK_DATA = false;

export const authUtils = {
  saveTokens(tokens) {
    if (tokens.access_token) localStorage.setItem('access_token', tokens.access_token)
    if (tokens.refresh_token) localStorage.setItem('refresh_token', tokens.refresh_token)
  },
  getTokens() {
    return {
      access_token: localStorage.getItem('access_token'),
      refresh_token: localStorage.getItem('refresh_token')
    }
  },
  clearTokens() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },
  isAuthenticated() {
    return !!localStorage.getItem('access_token')
  }
}

// Вспомогательная функция для обработки ошибок
async function handleResponse(response) {
    if (response.status === 204) {
        return null;
    }
    if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        const errorMessage = errorBody.detail || `Ошибка: ${response.status} ${response.statusText}`;
        throw new Error(errorMessage);
    }
    return response.json();
}

export const api = {
  // --- AUTH ---
  async loginUser(credentials) {
    if (USE_MOCK_DATA) { /* mock */ }
    
    try {
      const response = await fetch(`${BASE_API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      })
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  },

  async registerUser(userData) {
      try {
        const response = await fetch(`${BASE_API_URL}/api/v1/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        })
        return await handleResponse(response);
      } catch (e) { throw e }
  },

  // --- VACANCIES ---
  async getMyVacancies() {
    try {
      const tokens = authUtils.getTokens();
      const response = await fetch(`${BASE_API_URL}/api/v1/vacancies/my`, {
        headers: { 'Authorization': `Bearer ${tokens.access_token}` }
      });
      return await handleResponse(response);
    } catch (e) { throw e; }
  },

  async createVacancy(data) {
    const tokens = authUtils.getTokens();
    const response = await fetch(`${BASE_API_URL}/api/v1/vacancies/`, {
      method: 'POST',
      headers: { 
          'Authorization': `Bearer ${tokens.access_token}`,
          'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    return await handleResponse(response);
  },

  /**
   * КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Добавлена функция для обновления вакансии
   * Используется для редактирования полей и для закрытия (изменения статуса)
   */
  async updateVacancy(id, data) {
    const tokens = authUtils.getTokens();
    
    if (!tokens.access_token) {
        throw new Error("401: Отсутствует токен аутентификации.");
    }

    try {
      const response = await fetch(`${BASE_API_URL}/api/v1/vacancies/${id}`, {
        method: 'PATCH', // PATCH используется для частичного обновления ресурса
        headers: { 
            'Authorization': `Bearer ${tokens.access_token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
      return await handleResponse(response);
    } catch (e) { 
        console.error('Error updating vacancy:', e);
        throw e; 
    }
  },

 
  // !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Удалить вакансию !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  async deleteVacancy(vacancyId) {
    const tokens = authUtils.getTokens();
  
    if (!tokens.access_token) {
      throw new Error("401: Отсутствует токен аутентификации.");
    }

    try {
      // Используем новый эндпоинт /delete/{vacancy_id}
      const response = await fetch(`${BASE_API_URL}/api/v1/vacancies/delete/${vacancyId}`, {
        method: 'DELETE', 
        headers: { 
            'Authorization': `Bearer ${tokens.access_token}`,
        },
      });
      // Ожидаем 204 No Content
      return await handleResponse(response); 
    } catch (e) { 
        console.error('Error deleting vacancy:', e);
        throw e; 
    }
  },

  async getVacancyById(id) {
    // Публичный роут или приватный, лучше добавить токен если есть
    const tokens = authUtils.getTokens();
    const headers = {};
    if (tokens.access_token) headers['Authorization'] = `Bearer ${tokens.access_token}`;

    const response = await fetch(`${BASE_API_URL}/api/v1/vacancies/${id}`, { headers });
    return await handleResponse(response);
  },

  // --- CANDIDATES ---
  async getCandidatesForVacancy(vacancyId) {
    const tokens = authUtils.getTokens();
    if (!tokens.access_token) throw new Error('Not authenticated');

    const response = await fetch(`${BASE_API_URL}/api/v1/vacancies/${vacancyId}/candidates`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${tokens.access_token}`,
        'Content-Type': 'application/json',
      }
    });

    return await handleResponse(response);
  },
    
  // --- RESUME AND CANDIDATE MANAGEMENT (FROM CANDIDATE FRONTEND) ---
  
  // Имитация uploadResume: должен быть реализован для работы компонента
  async uploadResume(formData) {
    // Этот метод не был предоставлен, но необходим для ResumeAnalysisView.vue
    // Предполагаем, что он отправляет файл и данные пользователя
    const tokens = authUtils.getTokens(); // Если это приватный роут
    const headers = {};
    if (tokens.access_token) headers['Authorization'] = `Bearer ${tokens.access_token}`;

    const response = await fetch(`${BASE_API_URL}/api/v1/resume/upload`, {
        method: 'POST',
        // FormData автоматически устанавливает Content-Type: multipart/form-data
        // Поэтому Content-Type не добавляем вручную
        headers: headers,
        body: formData
    });
    return await handleResponse(response);
  },

  // Имитация createCandidate: должен быть реализован для работы компонента
  async createCandidate(candidateData) {
    // Этот метод не был предоставлен, но необходим для ResumeAnalysisView.vue
    // Предполагаем, что он отправляет данные кандидата
    const response = await fetch(`${BASE_API_URL}/api/v1/candidates/`, {
        method: 'POST',
        headers: { 
            // Это публичный роут (отправляется без токена работодателя),
            // FormData автоматически устанавливает Content-Type: multipart/form-data
        },
        body: candidateData 
    });
    return await handleResponse(response);
  },
}