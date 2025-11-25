const API_BASE_URL = 'http://localhost:8001'

export const api = {
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