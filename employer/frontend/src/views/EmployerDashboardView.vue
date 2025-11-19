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

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <h3>Активные вакансии</h3>
            <p class="stat-number">0</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-content">
            <h3>Всего кандидатов</h3>
            <p class="stat-number">0</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">✅</div>
          <div class="stat-content">
            <h3>Пройдено собеседований</h3>
            <p class="stat-number">0</p>
          </div>
        </div>
      </div>

      <div class="quick-actions">
        <h2>Быстрые действия</h2>
        <div class="actions-grid">
          <div class="action-card" @click="navigateToVacancies">
            <div class="action-icon">➕</div>
            <h3>Список вакансий</h3>
            <p>Посмотреть список текущих вакансий</p>
          </div>

          <div class="action-card" @click="navigateToCandidates">
            <div class="action-icon">👀</div>
            <h3>Просмотр кандидатов</h3>
            <p>Посмотрите всех кандидатов и результаты собеседований</p>
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

    </div>
  </div>
</template>

<script>
import { api, authUtils } from '@/utils/api'

export default {
  name: 'EmployerDashboardView',

  //Данные для вакансий
  data() {
    return {
      loading: false,
      error: null,
      vacancies: [], // 👈 ДОБАВИТЬ ЭТО
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
      this.$router.push({ name: 'employer-vacancies' });
      
    },
    
    navigateToCandidates() {
      // Здесь будет навигация к кандидатам
    }
  },
  
  async mounted() {
    // Проверяем авторизацию
    if (!authUtils.isAuthenticated()) {
      this.$router.push({ name: 'employer-login' })
    }
    
    // Загружаем данные дашборда
    await this.loadDashboardData()
  },

  async loadDashboardData() {
      this.loading = true
      this.error = null
      
      try {
        // Загружаем вакансии для статистики
        this.vacancies = await api.getMyVacancies() // 👈 СОХРАНЯЕМ ВАКАНСИИ
        
        // Обновляем статистику
        this.stats.totalVacancies = this.vacancies.length
        this.stats.activeVacancies = this.vacancies.filter(v => v.status === 'active').length
        
        // TODO: Загрузить реальные данные о кандидатах и откликах
        // Временные моковые данные
        this.stats.totalCandidates = 12
        this.stats.newApplications = 3
        
        // Генерируем последние активности
        this.generateRecentActivities(this.vacancies) // 👈 ПЕРЕДАЕМ СОХРАНЕННЫЕ ВАКАНСИИ
        
      } catch (error) {
        console.error('Error loading dashboard data:', error)
        this.error = 'Не удалось загрузить данные дашборда. Проверьте подключение к интернету.'
      } finally {
        this.loading = false
      }
    },

    // generateRecentActivities(vacancies) {
    //   const activities = []
      
    //   // Добавляем активности на основе вакансий
    //   vacancies.slice(0, 3).forEach(vacancy => {
    //     activities.push({
    //       id: `vacancy-${vacancy.vacancy_id}`,
    //       type: 'vacancy',
    //       text: `Создана вакансия "${vacancy.title}"`,
    //       time: this.formatTime(vacancy.created_at)
    //     })
    //   })
      
    //   // Добавляем моковые активности
    //   activities.push(
    //     {
    //       id: 'candidate-1',
    //       type: 'candidate',
    //       text: 'Новый отклик на вакансию "Frontend Developer"',
    //       time: '2 часа назад'
    //     },
    //     {
    //       id: 'interview-1',
    //       type: 'interview',
    //       text: 'Запланировано собеседование с Иваном Петровым',
    //       time: 'Вчера'
    //     }
    //   )
      
    //   this.recentActivities = activities
    // },

    // formatTime(dateString) {
    //   const date = new Date(dateString)
    //   const now = new Date()
    //   const diffMs = now - date
    //   const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
      
    //   if (diffDays === 0) {
    //     return 'Сегодня'
    //   } else if (diffDays === 1) {
    //     return 'Вчера'
    //   } else if (diffDays < 7) {
    //     return `${diffDays} дня назад`
    //   } else {
    //     return date.toLocaleDateString('ru-RU')
    //   }
    // },

    // getActivityIcon(type) {
    //   const icons = {
    //     vacancy: '📋',
    //     candidate: '👤',
    //     interview: '🎯',
    //     default: '📝'
    //   }
    //   return icons[type] || icons.default
    // }
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
}

.stat-icon {
  font-size: 2rem;
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
