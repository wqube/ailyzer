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
    </div>
  </div>
</template>

<script>
import { api, authUtils } from '@/utils/api'

export default {
  name: 'EmployerDashboardView',
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
      // Здесь будет навигация к созданию вакансий
      // alert('Функционал создания вакансий будет реализован позже')
    },
    
    navigateToCandidates() {
      // Здесь будет навигация к кандидатам
      alert('Функционал просмотра кандидатов будет реализован позже')
    }
  },
  
  mounted() {
    // Проверяем авторизацию
    if (!authUtils.isAuthenticated()) {
      this.$router.push({ name: 'employer-login' })
    }
    
    // Здесь можно загружать данные дашборда
    // await this.loadDashboardData()
  }
}
</script>

<style scoped>
.employer-dashboard {
  min-height: 80vh;
  padding: 2rem 0;
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

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>