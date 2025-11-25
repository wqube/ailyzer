<template>
  <div class="candidates-view">
    <div class="candidates-header">
      <div class="container">
        <h1>Кандидаты на вакансию: {{ currentVacancy?.title }}</h1>
        <button @click="$router.back()" class="btn btn-outline">
          Назад к вакансиям
        </button>
      </div>
    </div>

    <div class="candidates-content">
      <div class="container">
        <!-- Индикатор загрузки -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Загрузка кандидатов...</p>
        </div>

        <!-- Список кандидатов -->
        <div class="candidates-list" v-else-if="candidates.length > 0">
          <div 
            v-for="candidate in candidates" 
            :key="candidate.id" 
            class="candidate-card"
          >
            <div class="candidate-header">
              <h3>{{ candidate.full_name }}</h3>
              <span :class="['candidate-status', candidate.status]">
                {{ getStatusText(candidate.status) }}
              </span>
            </div>
            
            <div class="candidate-info">
              <p><strong>Email:</strong> {{ candidate.email }}</p>
              <p><strong>Телефон:</strong> {{ candidate.phone || 'Не указан' }}</p>
              <p><strong>Опыт работы:</strong> {{ candidate.experience || 'Не указан' }}</p>
              <p><strong>Навыки:</strong> {{ candidate.skills || 'Не указаны' }}</p>
              <p><strong>Дата отклика:</strong> {{ formatDate(candidate.applied_at) }}</p>
            </div>
            
            <div class="candidate-actions">
              <button 
                @click="viewCandidateDetails(candidate)" 
                class="btn btn-outline"
              >
                Подробнее
              </button>
              <button 
                @click="downloadResume(candidate)" 
                class="btn btn-primary"
                v-if="candidate.resume_url"
              >
                Скачать резюме
              </button>
            </div>
          </div>
        </div>

        <!-- Сообщение если кандидатов нет -->
        <div v-else class="empty-state">
          <div class="empty-icon">👥</div>
          <h3>Пока нет кандидатов</h3>
          <p>На эту вакансию еще никто не откликнулся</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api, authUtils } from '@/utils/api'

export default {
  name: 'CandidatesView',
  data() {
    return {
      candidates: [],
      currentVacancy: null,
      loading: false,
      errorMessage: ''
    }
  },
  methods: {
    // Загрузка кандидатов для вакансии
    async loadCandidates() {
      this.loading = true
      this.errorMessage = ''
      
      try {
        const vacancyId = this.$route.params.vacancyId
        // Загружаем данные вакансии
        this.currentVacancy = await api.getVacancyById(vacancyId)
        
        // TODO: Заменить на реальный API вызов для получения кандидатов
        // Временные моковые данные
        this.candidates = [
          {
            id: 1,
            full_name: 'Иванов Иван Иванович',
            email: 'ivanov@example.com',
            phone: '+7 (999) 123-45-67',
            experience: '3 года',
            skills: 'Vue.js, JavaScript, HTML, CSS',
            status: 'new',
            applied_at: '2024-01-20T10:30:00',
            resume_url: '/resumes/resume1.pdf'
          },
          {
            id: 2,
            full_name: 'Петрова Анна Сергеевна',
            email: 'petrova@example.com',
            phone: '+7 (999) 765-43-21',
            experience: '2 года',
            skills: 'React, TypeScript, Redux',
            status: 'reviewed',
            applied_at: '2024-01-19T14:20:00'
          }
        ]
        
      } catch (error) {
        console.error('Error loading candidates:', error)
        this.errorMessage = this.getErrorMessage(error)
      } finally {
        this.loading = false
      }
    },

    // Просмотр деталей кандидата
    viewCandidateDetails(candidate) {
      // Здесь можно открыть модальное окно с детальной информацией
      // или перейти на отдельную страницу кандидата
      console.log('View candidate details:', candidate)
      // Временная реализация - показываем alert
      alert(`Детальная информация о кандидате:\n\nИмя: ${candidate.full_name}\nEmail: ${candidate.email}\nТелефон: ${candidate.phone}\nОпыт: ${candidate.experience}\nНавыки: ${candidate.skills}`)
    },

    // Скачать резюме
    downloadResume(candidate) {
      if (candidate.resume_url) {
        // Эмуляция скачивания резюме
        const link = document.createElement('a')
        link.href = candidate.resume_url
        link.download = `resume_${candidate.full_name}.pdf`
        link.click()
      }
    },

    // Обработка ошибок
    getErrorMessage(error) {
      const message = error.message || 'Произошла ошибка'
      
      if (message.includes('401') || message.includes('authentication')) {
        return 'Ошибка авторизации. Пожалуйста, войдите снова.'
      } else if (message.includes('404')) {
        return 'Вакансия не найдена.'
      }
      
      return message
    },

    // Форматирование даты
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('ru-RU')
    },

    // Текст статуса
    getStatusText(status) {
      const statusMap = {
        new: 'Новый',
        reviewed: 'Просмотрен',
        rejected: 'Отклонен',
        invited: 'Приглашен'
      }
      return statusMap[status] || status
    }
  },

  mounted() {
    // Проверяем авторизацию
    if (!authUtils.isAuthenticated()) {
      this.$router.push({ name: 'employer-login' })
      return
    }
    
    this.loadCandidates()
  }
}
</script>

<style scoped>
.candidates-view {
  min-height: 80vh;
}

.candidates-header {
  background: white;
  padding: 2rem 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 2rem;
}

.candidates-header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.candidates-header h1 {
  color: #333;
  margin: 0;
}

.candidates-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.candidate-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #8B5FBF;
}

.candidate-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.candidate-header h3 {
  margin: 0;
  color: #333;
  flex: 1;
}

.candidate-status {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.candidate-status.new {
  background: #e7f7ef;
  color: #10b981;
}

.candidate-status.reviewed {
  background: #eef4ff;
  color: #3b82f6;
}

.candidate-status.rejected {
  background: #fef3f2;
  color: #f04444;
}

.candidate-status.invited {
  background: #fdf6e3;
  color: #d97706;
}

.candidate-info {
  margin-bottom: 1.5rem;
}

.candidate-info p {
  margin: 0.5rem 0;
  color: #666;
}

.candidate-actions {
  display: flex;
  gap: 0.5rem;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.empty-state p {
  margin: 0 0 1.5rem 0;
  color: #666;
}

.loading-state {
  text-align: center;
  padding: 3rem 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
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

@media (max-width: 768px) {
  .candidates-header .container {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .candidate-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .candidate-actions {
    flex-direction: column;
  }
}
</style>