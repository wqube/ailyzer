<template>
  <div class="employer-dashboard">
    <div class="dashboard-header">
      <h1>Дашборд работодателя</h1>
    </div>

    <div class="dashboard-content">
      <div class="welcome-section">
        <h2>Добро пожаловать в AIlyzer!</h2>
        <p>Используйте панель управления для управления вашими вакансиями и кандидатами.</p>
      </div>

      <!-- Индикатор загрузки -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Загрузка данных...</p>
      </div>

      <template v-else>
        <!-- Сообщение об ошибке -->
        <div v-if="error" class="error-notification">
          <div class="error-content">
            <span>{{ error }}</span>
            <button @click="error = ''" class="btn-close-small">&times;</button>
          </div>
        </div>

        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">📋</div>
            <div class="stat-content">
              <h3>Всего вакансий</h3>
              <p class="stat-number">{{ stats.totalVacancies }}</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-content">
              <h3>Активные вакансии</h3>
              <p class="stat-number">{{ stats.activeVacancies }}</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-content">
              <h3>Всего кандидатов</h3>
              <p class="stat-number">{{ stats.totalCandidates }}</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">🎯</div>
            <div class="stat-content">
              <h3>Новые отклики</h3>
              <p class="stat-number">{{ stats.newApplications }}</p>
            </div>
          </div>
        </div>

        <div class="quick-actions">
          <h2>Быстрые действия</h2>
          <div class="actions-grid">
            <div class="action-card" @click="navigateToVacancies">
              <div class="action-icon">📋</div>
              <h3>Список вакансий</h3>
              <p>Посмотреть и управлять вашими вакансиями</p>
            </div>

            <div class="action-card" @click="navigateToCreateVacancy">
              <div class="action-icon">➕</div>
              <h3>Создать вакансию</h3>
              <p>Добавить новую вакансию для поиска кандидатов</p>
            </div>
          </div>
        </div>

        <div class="recent-activities" v-if="recentActivities.length > 0">
          <h2>Последние активности</h2>
          <div class="activities-list">
            <div 
              v-for="activity in recentActivities" 
              :key="activity.id"
              class="activity-item"
            >
              <div class="activity-icon" :class="activity.type">
                {{ getActivityIcon(activity.type) }}
              </div>
              <div class="activity-content">
                <p class="activity-text">{{ activity.text }}</p>
                <span class="activity-time">{{ activity.time }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { api, authUtils } from '@/utils/api'

export default {
  name: 'EmployerDashboardView',

  data() {
    return {
      loading: false,
      error: null,
      vacancies: [],
      candidates: [],
      stats: {
        totalVacancies: 0,
        activeVacancies: 0,
        totalCandidates: 0,
        newApplications: 0
      },
      recentActivities: []
    }
  },

  methods: {
    async handleLogout() {
      try {
        const tokens = authUtils.getTokens()
        if (tokens.refresh_token) {
          await api.logoutUser(tokens.refresh_token)
        }
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        authUtils.clearTokens()
        this.$router.push({ name: 'employer-login' })
      }
    },
    
    navigateToVacancies() {
      this.$router.push({ name: 'employer-vacancies' })
    },

    navigateToCreateVacancy() {
      this.$router.push({ name: 'employer-vacancies' })
    },

    async loadDashboardData() {
      this.loading = true
      this.error = null
      
      try {
        // 1. Загружаем вакансии
        this.vacancies = await api.getMyVacancies()
        
        // 2. Загружаем кандидатов для каждой вакансии
        this.candidates = []
        for (const vacancy of this.vacancies) {
          try {
            const vacancyCandidates = await api.getCandidatesForVacancy(vacancy.id)
            this.candidates = [...this.candidates, ...vacancyCandidates]
          } catch (error) {
            console.error(`Error loading candidates for vacancy ${vacancy.id}:`, error)
          }
        }
        
        // 3. Рассчитываем статистику
        this.calculateStats()
        
        // 4. Генерируем последние активности
        this.generateRecentActivities()
        
      } catch (error) {
        console.error('Error loading dashboard data:', error)
        this.error = 'Не удалось загрузить данные дашборда. Проверьте подключение к интернету.'
      } finally {
        this.loading = false
      }
    },

    calculateStats() {
      // Статистика по вакансиям
      this.stats.totalVacancies = this.vacancies.length
      this.stats.activeVacancies = this.vacancies.filter(v => v.status === 'active').length
      
      // Статистика по кандидатам
      this.stats.totalCandidates = this.candidates.length
      
      // Новые отклики (кандидаты за последние 7 дней)
      const weekAgo = new Date()
      weekAgo.setDate(weekAgo.getDate() - 7)
      this.stats.newApplications = this.candidates.filter(candidate => {
        const createdAt = new Date(candidate.created_at)
        return createdAt >= weekAgo
      }).length
    },

    generateRecentActivities() {
      const activities = []
      
      // Добавляем активности на основе последних вакансий
      this.vacancies.slice(0, 3).forEach(vacancy => {
        activities.push({
          id: `vacancy-${vacancy.id}`,
          type: 'vacancy',
          text: `Создана вакансия "${vacancy.title}"`,
          time: this.formatTime(vacancy.created_at)
        })
      })
      
      // Добавляем активности на основе последних кандидатов
      this.candidates.slice(0, 2).forEach(candidate => {
        const vacancy = this.vacancies.find(v => v.id === candidate.vacancy_id)
        const vacancyTitle = vacancy ? vacancy.title : 'неизвестная вакансия'
        activities.push({
          id: `candidate-${candidate.id}`,
          type: 'candidate',
          text: `Новый отклик на вакансию "${vacancyTitle}" от ${candidate.full_name || candidate.email}`,
          time: this.formatTime(candidate.created_at)
        })
      })
      
      // Если активностей мало, добавляем информационные
      if (activities.length < 3) {
        activities.push({
          id: 'welcome-1',
          type: 'info',
          text: 'Добро пожаловать в AIlyzer! Начните с создания вашей первой вакансии.',
          time: 'Только что'
        })
      }
      
      this.recentActivities = activities.slice(0, 5) // Ограничиваем 5 активностями
    },

    formatTime(dateString) {
      if (!dateString) return 'Недавно'
      
      try {
        const date = new Date(dateString)
        const now = new Date()
        const diffMs = now - date
        const diffMinutes = Math.floor(diffMs / (1000 * 60))
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
        
        if (diffMinutes < 60) {
          return `${diffMinutes} мин. назад`
        } else if (diffHours < 24) {
          return `${diffHours} ч. назад`
        } else if (diffDays === 1) {
          return 'Вчера'
        } else if (diffDays < 7) {
          return `${diffDays} дн. назад`
        } else {
          return date.toLocaleDateString('ru-RU')
        }
      } catch {
        return 'Недавно'
      }
    },

    getActivityIcon(type) {
      const icons = {
        vacancy: '📋',
        candidate: '👤',
        interview: '🎯',
        info: 'ℹ️',
        default: '📝'
      }
      return icons[type] || icons.default
    }
  },
  
  async mounted() {
    // Проверяем авторизацию
    if (!authUtils.isAuthenticated()) {
      this.$router.push({ name: 'employer-login' })
      return
    }
    
    // Загружаем данные дашборда
    await this.loadDashboardData()
  }
}
</script>

<style scoped>
/* Существующие стили остаются такими же, но добавлю стили для индикаторов */

.employer-dashboard {
  min-height: 80vh;
  padding: 2rem 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.dashboard-header h1 {
  color: #333;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.welcome-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.welcome-section h2 {
  margin: 0 0 0.5rem 0;
}

.welcome-section p {
  margin: 0;
  opacity: 0.9;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-content h3 {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
  color: #666;
  font-weight: normal;
}

.stat-number {
  margin: 0;
  font-size: 2rem;
  font-weight: bold;
  color: #333;
}

.quick-actions h2 {
  margin-bottom: 1rem;
  color: #333;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.action-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
}

.action-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.action-card h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.action-card p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

.recent-activities {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-top: 2rem;
}

.recent-activities h2 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.5rem;
}

.activities-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  border-radius: 8px;
  background: #f8f9fa;
  border-left: 4px solid #8B5FBF;
}

.activity-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-text {
  margin: 0 0 0.25rem 0;
  color: #333;
  font-size: 0.9rem;
}

.activity-time {
  color: #666;
  font-size: 0.8rem;
}

/* Стили для индикаторов загрузки и ошибок */
.loading-state {
  text-align: center;
  padding: 3rem 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin: 2rem 0;
}

.loading-spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #8B5FBF;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-notification {
  background: #fef3f2;
  border: 1px solid #fecdca;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.error-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #d92d20;
  font-weight: 500;
}

.btn-close-small {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #d92d20;
}

@media (max-width: 768px) {
  .employer-dashboard {
    padding: 1rem 0.5rem;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .welcome-section {
    padding: 1.5rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .employer-dashboard {
    padding: 1rem 0.25rem;
  }
  
  .welcome-section {
    padding: 1rem;
  }
  
  .stat-card,
  .action-card {
    padding: 1rem;
  }
}
</style>