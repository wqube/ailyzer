// !!! ВАЖНАЯ НАСТРОЙКА: БАЗОВЫЙ URL API !!!

// Определяем базовый URL в зависимости от среды:
// 1. Если это локальная разработка (например, localhost), используем локальный бэкенд.
// 2. Если это продакшн, используем публичный домен API.

let API_BASE_URL;

// Проверяем, запущен ли фронтенд локально 
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    // Используем локальный адрес бэкенда для разработки (Candidate обычно на 8001)
    API_BASE_URL = 'http://localhost:8001';
} else {
    // !!! ЗАМЕНИТЕ ЭТОТ АДРЕС НА ВАШ ПРОДАКШН-ДОМЕН API !!!
    // Например: https://api.ailyzer.ru
    API_BASE_URL = 'https://api.ailyzer.ru'; 
}
// ----------------------------------------------------

// NOTE: authUtils is assumed to be available globally or imported in the actual environment
// Этот файл содержит только определение объекта `api`.

export const api = {
  // Employer Management - Vacancies (НЕОБХОДИМ ДЛЯ ДАШБОРДА)
  async getMyVacancies() {
    try {
      const tokens = authUtils.getTokens()
      if (!tokens.access_token) {
        throw new Error('Нет токена доступа. Требуется авторизация.');
      }

      const response = await fetch(`${API_BASE_URL}/api/vacancies/my`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${tokens.access_token}`,
        }
      })

      if (response.status === 401) {
          throw new Error('Не авторизован. Токен истек или недействителен.');
      }
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Get my vacancies error:', error)
      throw new Error('Не удалось загрузить ваши вакансии.')
    }
  },
    
  // 🚨 ОБНОВЛЕН: Улучшенная обработка ошибок для диагностики
  async getCandidatesForVacancy(vacancyId) {
    try {
      const tokens = authUtils.getTokens()
      if (!tokens.access_token) {
        console.error(`[Candidates API] Vacancy ${vacancyId}: Токен отсутствует.`);
        throw new Error('Нет токена доступа. Требуется авторизация.');
      }

      const response = await fetch(`${API_BASE_URL}/api/candidates/vacancy/${vacancyId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${tokens.access_token}`,
          'Content-Type': 'application/json',
        }
      })
      
      if (response.status === 401) {
        // Явное логирование 401
        console.error(`[Candidates API] Vacancy ${vacancyId}: Ошибка 401 Unauthorized. Проверьте токен.`);
        throw new Error(`Unauthorized (401) fetching candidates for vacancy ${vacancyId}`);
      }
      
      if (!response.ok) {
        const errorDetail = await response.text();
        console.error(`[Candidates API] Vacancy ${vacancyId}: Ошибка HTTP ${response.status}. Детали:`, errorDetail);
        throw new Error(`HTTP error fetching candidates: ${response.status}`);
      }
      
      const candidates = await response.json();
      console.log(`[Candidates API] Vacancy ${vacancyId}: Успешно загружено ${candidates.length} кандидатов.`);
      return candidates;
    } catch (error) {
      console.error(`[Candidates API] Общая ошибка загрузки кандидатов для вакансии ${vacancyId}:`, error);
      // Возвращаем пустой массив, чтобы дашборд не ломался
      return []; 
    }
  },


  // Загрузка резюме
  async uploadResume(formData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/upload-resume`, {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Upload error:', error)
      throw new Error('Не удалось подключиться к серверу. Проверьте, запущен ли бэкенд.')
    }
  },

  // НОВЫЙ МЕТОД: Получение вакансии по ID
  async getVacancyById(vacancyId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/vacancies/${vacancyId}`, {
        method: 'GET'
      })
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Вакансия не найдена')
        }
        if (response.status === 400) {
          throw new Error('Вакансия неактивна')
        }
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Get vacancy error:', error)
      throw error
    }
  },

  // Интервью
  async startInterview(interviewData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/start_interview`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(interviewData)
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP error! status: ${response.status}, details: ${errorText}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Start interview error:', error)
      throw new Error('Не удалось начать собеседование. Проверьте подключение к серверу.')
    }
  },

  async sendAnswer(answerData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(answerData)
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP error! status: ${response.status}, details: ${errorText}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Send answer error:', error)
      throw new Error('Не удалось отправить ответ. Проверьте подключение к серверу.')
    }
  },

  // Создание кандидата
  async createCandidate(formData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/candidates/create`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP error! status: ${response.status}, details: ${errorText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Create candidate error:', error)
      throw new Error('Не удалось сохранить кандидата. Проверьте подключение к серверу.')
    }
  },
}

export const handleApiError = (error) => {
  console.error('API Error:', error)
  return {
    success: false,
    error: error.message || 'Произошла ошибка при выполнении запроса'
  }
}