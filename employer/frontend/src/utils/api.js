const API_BASE_URL = 'http://localhost:8000'

// Флаг для использования mock данных
const USE_MOCK_DATA = true;

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
    }
}

// Вспомогательные функции для работы с аутентификацией
export const authUtils = {
// Сохранение токенов в localStorage
saveTokens(tokens) {
        if (tokens.access_token) {
            localStorage.setItem('access_token', tokens.access_token)
        }
        if (tokens.refresh_token) {
            localStorage.setItem('refresh_token', tokens.refresh_token)
        }
    },

    // Получение токенов из localStorage
    getTokens() {
        return {
        access_token: localStorage.getItem('access_token'),
        refresh_token: localStorage.getItem('refresh_token')
        }
    },

    // Удаление токенов (при выходе)
    clearTokens() {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
    },

    // Проверка, авторизован ли пользователь
    isAuthenticated() {
        return !!localStorage.getItem('access_token')
    }
}
