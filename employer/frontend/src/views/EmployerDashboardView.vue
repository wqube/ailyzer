<template>
  <div class="employer-dashboard">
    <!-- Заголовок с кнопкой выхода -->
    <div class="dashboard-header">
      <div class="header-content">
        <h1>Дашборд работодателя</h1>
        <button 
          @click="handleLogout" 
          class="logout-btn"
          title="Выйти из системы"
        >
          <span class="btn-text">Выйти</span>
          <span class="btn-icon">🚪</span>
        </button>
      </div>
    </div>

    <!-- Основной контент -->
    <div class="dashboard-content">
      <!-- Приветственная секция -->
      <div class="welcome-section">
        <h2>Добро пожаловать в AIlyzer!</h2>
        <p>Используйте панель управления для управления вашими вакансиями и кандидатами.</p>
      </div>

      <!-- Статистика -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">📊</div>
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
          <div class="stat-icon">🆕</div>
          <div class="stat-content">
            <h3>Новых откликов</h3>
            <p class="stat-number">{{ stats.newApplications }}</p>
          </div>
        </div>
      </div>

      <!-- Быстрые действия -->
      <div class="quick-actions">
        <h2>Быстрые действия</h2>
        <div class="actions-grid">
          <div class="action-card" @click="navigateToVacancies">
            <div class="action-icon">📋</div>
            <div class="action-content">
              <h3>Мои вакансии</h3>
              <p>Управляйте созданными вакансиями, редактируйте и просматривайте отклики</p>
            </div>
          </div>

          <div class="action-card" @click="navigateToCreateVacancy">
            <div class="action-icon">➕</div>
            <div class="action-content">
              <h3>Создать вакансию</h3>
              <p>Добавьте новую вакансию для привлечения кандидатов</p>
            </div>
          </div>

          <div class="action-card" @click="navigateToCandidates">
            <div class="action-icon">👀</div>
            <div class="action-content">
              <h3>Кандидаты</h3>
              <p>Просматривайте всех кандидатов и результаты собеседований</p>
            </div>
          </div>

          <div class="action-card" @click="navigateToAnalytics">
            <div class="action-icon">📈</div>
            <div class="action-content">
              <h3>Аналитика</h3>
              <p>Статистика и аналитика по вакансиям и кандидатам</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Последние активности -->
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

      <!-- Состояние загрузки -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Загрузка данных...</p>
      </div>

      <!-- Состояние ошибки -->
      <div v-if="error" class="error-state">
        <div class="error-icon">⚠️</div>
        <h3>Ошибка загрузки</h3>
        <p>{{ error }}</p>
        <button @click="loadDashboardData" class="retry-btn">Попробовать снова</button>
      </div>
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
      this.$router.push({ name: 'create-vacancy' })
    },
    
    navigateToCandidates() {
      this.$router.push({ name: 'candidates' })
    },
    
    navigateToAnalytics() {
      this.$router.push({ name: 'analytics' })
    },

    async loadDashboardData() {
      this.loading = true
      this.error = null
      
      try {
        // Загружаем вакансии для статистики
        const vacancies = await api.getMyVacancies()
        
        // Обновляем статистику
        this.stats.totalVacancies = vacancies.length
        this.stats.activeVacancies = vacancies.filter(v => v.status === 'active').length
        
        // TODO: Загрузить реальные данные о кандидатах и откликах
        // Временные моковые данные
        this.stats.totalCandidates = 12
        this.stats.newApplications = 3
        
        // Генерируем последние активности
        this.generateRecentActivities(vacancies)
        
      } catch (error) {
        console.error('Error loading dashboard data:', error)
        this.error = 'Не удалось загрузить данные дашборда. Проверьте подключение к интернету.'
      } finally {
        this.loading = false
      }
    },

    generateRecentActivities(vacancies) {
      const activities = []
      
      // Добавляем активности на основе вакансий
      vacancies.slice(0, 3).forEach(vacancy => {
        activities.push({
          id: `vacancy-${vacancy.vacancy_id}`,
          type: 'vacancy',
          text: `Создана вакансия "${vacancy.title}"`,
          time: this.formatTime(vacancy.created_at)
        })
      })
      
      // Добавляем моковые активности
      activities.push(
        {
          id: 'candidate-1',
          type: 'candidate',
          text: 'Новый отклик на вакансию "Frontend Developer"',
          time: '2 часа назад'
        },
        {
          id: 'interview-1',
          type: 'interview',
          text: 'Запланировано собеседование с Иваном Петровым',
          time: 'Вчера'
        }
      )
      
      this.recentActivities = activities
    },

    formatTime(dateString) {
      const date = new Date(dateString)
      const now = new Date()
      const diffMs = now - date
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
      
      if (diffDays === 0) {
        return 'Сегодня'
      } else if (diffDays === 1) {
        return 'Вчера'
      } else if (diffDays < 7) {
        return `${diffDays} дня назад`
      } else {
        return date.toLocaleDateString('ru-RU')
      }
    },

    getActivityIcon(type) {
      const icons = {
        vacancy: '📋',
        candidate: '👤',
        interview: '🎯',
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
.employer-dashboard {
  min-height: 80vh;
  padding: 2rem 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dashboard-header h1 {
  color: #333;
  margin: 0;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: #e9ecef;
  border-color: #adb5bd;
}

.btn-text {
  font-size: 0.9rem;
}

.btn-icon {
  font-size: 1rem;
}

.welcome-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  border-radius: 12px;
  margin-bottom: 2rem;
}

.welcome-section h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
}

.welcome-section p {
  margin: 0;
  opacity: 0.9;
  font-size: 1rem;
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
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
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

.quick-actions {
  margin-bottom: 2rem;
}

.quick-actions h2 {
  margin-bottom: 1.5rem;
  color: #333;
  font-size: 1.5rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.action-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
}

.action-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.action-content h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1.1rem;
}

.action-content p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
}

.recent-activities {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
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

.loading-state,
.error-state {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-state h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.error-state p {
  margin: 0 0 1.5rem 0;
  color: #666;
}

.retry-btn {
  padding: 0.75rem 1.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #5a6fd8;
}

@media (max-width: 768px) {
  .employer-dashboard {
    padding: 1rem 0.5rem;
  }
  
  .header-content {
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
  
  .action-card {
    flex-direction: column;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .employer-dashboard {
    padding: 1rem 0.25rem;
  }
  
  .welcome-section {
    padding: 1rem;
  }
  
  .welcome-section h2 {
    font-size: 1.3rem;
  }
  
  .stat-card,
  .action-card {
    padding: 1rem;
  }
  
  .activity-item {
    padding: 0.75rem;
  }
}
</style>