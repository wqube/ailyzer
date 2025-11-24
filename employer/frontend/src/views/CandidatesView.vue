<template>
  <div class="candidates-view">
    <div class="candidates-header">
      <div class="container">
        <div class="header-content">
          <h1>Кандидаты по вакансии</h1>
          <button @click="$router.back()" class="btn btn-outline">
            ← Назад к вакансиям
          </button>
        </div>
      </div>
    </div>

    <div class="candidates-content">
      <div class="container">
        <!-- Информация о вакансии -->
        <div v-if="vacancy" class="vacancy-info-card">
          <h2>{{ vacancy.title }}</h2>
          <div class="vacancy-details">
            <p><strong>Уровень:</strong> {{ getLevelText(vacancy.level) }}</p>
            <p><strong>Статус:</strong> 
              <span :class="['status-badge', vacancy.status]">
                {{ getStatusText(vacancy.status) }}
              </span>
            </p>
            <p><strong>Описание:</strong> {{ vacancy.description }}</p>
            <p><strong>Требования:</strong> {{ vacancy.requirements }}</p>
          </div>
        </div>

        <!-- Список кандидатов -->
        <div class="candidates-section">
          <div class="section-header">
            <h2>Кандидаты ({{ candidates.length }})</h2>
          </div>

          <div v-if="loading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>Загрузка кандидатов...</p>
          </div>

          <div v-else-if="candidates.length > 0" class="candidates-list">
            <div 
              v-for="candidate in candidates" 
              :key="candidate.candidate_id || candidate.id"
              class="candidate-card"
            >
              <div class="candidate-header">
                <h3>{{ candidate.name || candidate.email }}</h3>
                <span :class="['candidate-status', candidate.status]">
                  {{ getCandidateStatusText(candidate.status) }}
                </span>
              </div>
              
              <div class="candidate-info">
                <p><strong>Email:</strong> {{ candidate.email }}</p>
                <p><strong>Телефон:</strong> {{ candidate.phone || 'Не указан' }}</p>
                <p><strong>Резюме:</strong> {{ candidate.resume_text || 'Не прикреплено' }}</p>
                <p><strong>Дата отклика:</strong> {{ formatDate(candidate.created_at) }}</p>
              </div>
              
              <div class="candidate-actions">
                <button @click="viewCandidateDetails(candidate)" class="btn btn-outline">
                  Подробнее
                </button>
                <button @click="downloadResume(candidate)" class="btn btn-primary" 
                        v-if="candidate.resume_file">
                  Скачать резюме
                </button>
                <button @click="scheduleInterview(candidate)" class="btn btn-primary">
                  Назначить собеседование
                </button>
              </div>
            </div>
          </div>

          <div v-else class="empty-state">
            <div class="empty-icon">👥</div>
            <h3>Пока нет кандидатов</h3>
            <p>На эту вакансию еще не было откликов</p>
            <p>Поделитесь ссылкой на вакансию чтобы привлечь кандидатов</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно деталей кандидата -->
    <div v-if="selectedCandidate" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Подробности кандидата</h2>
          <button @click="selectedCandidate = null" class="btn-close">&times;</button>
        </div>
        
        <div class="candidate-details">
          <div class="detail-group">
            <label>Имя:</label>
            <span>{{ selectedCandidate.name || 'Не указано' }}</span>
          </div>
          <div class="detail-group">
            <label>Email:</label>
            <span>{{ selectedCandidate.email }}</span>
          </div>
          <div class="detail-group">
            <label>Телефон:</label>
            <span>{{ selectedCandidate.phone || 'Не указан' }}</span>
          </div>
          <div class="detail-group">
            <label>Статус:</label>
            <span :class="['status-badge', selectedCandidate.status]">
              {{ getCandidateStatusText(selectedCandidate.status) }}
            </span>
          </div>
          <div class="detail-group">
            <label>Дата отклика:</label>
            <span>{{ formatDate(selectedCandidate.created_at) }}</span>
          </div>
          <div class="detail-group full-width">
            <label>Резюме:</label>
            <div class="resume-text">
              {{ selectedCandidate.resume_text || 'Резюме не прикреплено' }}
            </div>
          </div>
        </div>
        
        <div class="modal-actions">
          <button @click="selectedCandidate = null" class="btn btn-outline">
            Закрыть
          </button>
          <button @click="scheduleInterview(selectedCandidate)" class="btn btn-primary">
            Назначить собеседование
          </button>
        </div>
      </div>
    </div>

    <div v-if="errorMessage" class="error-notification">
      <div class="container">
        <div class="error-content">
          <span>{{ errorMessage }}</span>
          <button @click="errorMessage = ''" class="btn-close-small">&times;</button>
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
      vacancy: null,
      candidates: [],
      loading: false,
      errorMessage: '',
      selectedCandidate: null
    }
  },
  methods: {
    async loadVacancyAndCandidates() {
  this.loading = true
  this.errorMessage = ''
  
  const vacancyId = this.$route.query.vacancy_id
  
  if (!vacancyId) {
    this.errorMessage = 'ID вакансии не указан'
    this.loading = false
    return
  }

  try {
    // Загружаем информацию о вакансии
    this.vacancy = await api.getVacancyById(vacancyId)
    
    // Загружаем кандидатов по вакансии
    this.candidates = await api.getCandidatesByVacancy(vacancyId)
    
  } catch (error) {
    console.error('Error loading data:', error)
    this.errorMessage = this.getErrorMessage(error)
    
    if (error.message.includes('401') || error.message.includes('authentication')) {
      this.$router.push({ name: 'employer-login' })
    }
  } finally {
    this.loading = false
  }
    },

    // И добавьте метод для обновления статуса кандидата:
async updateCandidateStatus(candidate, newStatus) {
  try {
    const updatedCandidate = await api.updateCandidateStatus(
      candidate.candidate_id, 
      this.vacancy.vacancy_id, 
      newStatus
    )
    
    // Обновляем кандидата в списке
    const index = this.candidates.findIndex(c => c.candidate_id === candidate.candidate_id)
    if (index !== -1) {
      this.candidates.splice(index, 1, updatedCandidate)
    }
    
    this.showSuccessMessage(`Статус кандидата обновлен на: ${this.getCandidateStatusText(newStatus)}`)
    
  } catch (error) {
    console.error('Error updating candidate status:', error)
    this.errorMessage = this.getErrorMessage(error)
  }
},

    viewCandidateDetails(candidate) {
      this.selectedCandidate = candidate
    },

    downloadResume(candidate) {
      // TODO: Реализовать скачивание резюме
      alert(`Скачивание резюме кандидата ${candidate.name}`)
    },

    scheduleInterview(candidate) {
      // TODO: Реализовать назначение собеседования
      alert(`Назначение собеседования с ${candidate.name}`)
    },

    getLevelText(level) {
      const levelMap = {
        junior: 'Junior',
        middle: 'Middle', 
        senior: 'Senior',
        lead: 'Lead'
      }
      return levelMap[level] || level
    },

    getStatusText(status) {
      const statusMap = {
        active: 'Активна',
        closed: 'Закрыта',
        draft: 'Черновик'
      }
      return statusMap[status] || status
    },

    getCandidateStatusText(status) {
      const statusMap = {
        new: 'Новый',
        reviewed: 'Просмотрен',
        interviewed: 'Собеседование',
        rejected: 'Отклонен',
        hired: 'Принят'
      }
      return statusMap[status] || status
    },

    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('ru-RU')
    },

    getErrorMessage(error) {
      const message = error.message || 'Произошла ошибка'
      
      if (message.includes('401') || message.includes('authentication')) {
        return 'Ошибка авторизации. Пожалуйста, войдите снова.'
      } else if (message.includes('network') || message.includes('fetch')) {
        return 'Ошибка соединения. Проверьте подключение к интернету.'
      } else if (message.includes('500')) {
        return 'Внутренняя ошибка сервера. Попробуйте позже.'
      } else if (message.includes('404')) {
        return 'Вакансия не найдена.'
      }
      
      return message
    }
  },

  mounted() {
    if (!authUtils.isAuthenticated()) {
      this.$router.push({ name: 'employer-login' })
      return
    }
    
    this.loadVacancyAndCandidates()
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

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  color: #333;
  margin: 0;
}

.vacancy-info-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  border-left: 4px solid #8B5FBF;
}

.vacancy-info-card h2 {
  margin: 0 0 1rem 0;
  color: #333;
}

.vacancy-details p {
  margin: 0.5rem 0;
  color: #666;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.active {
  background: #e7f7ef;
  color: #10b981;
}

.status-badge.closed {
  background: #fef3f2;
  color: #f04444;
}

.candidates-section {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.section-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.section-header h2 {
  margin: 0;
  color: #333;
}

.candidates-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.candidate-card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 1.5rem;
  transition: box-shadow 0.2s;
}

.candidate-card:hover {
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
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
  background: #e0f2fe;
  color: #0369a1;
}

.candidate-status.reviewed {
  background: #fef3c7;
  color: #d97706;
}

.candidate-status.interviewed {
  background: #dcfce7;
  color: #16a34a;
}

.candidate-status.rejected {
  background: #fef3f2;
  color: #dc2626;
}

.candidate-status.hired {
  background: #dcfce7;
  color: #16a34a;
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
  flex-wrap: wrap;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
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
  margin: 0 0 1rem 0;
  color: #666;
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.btn-close:hover {
  color: #333;
}

.candidate-details {
  padding: 1.5rem;
}

.detail-group {
  display: flex;
  margin-bottom: 1rem;
  align-items: flex-start;
}

.detail-group label {
  font-weight: 500;
  color: #333;
  min-width: 120px;
  margin-right: 1rem;
}

.detail-group span {
  color: #666;
  flex: 1;
}

.detail-group.full-width {
  flex-direction: column;
}

.detail-group.full-width label {
  margin-bottom: 0.5rem;
}

.resume-text {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  border: 1px solid #e9ecef;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}

.modal-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  padding: 1.5rem;
  border-top: 1px solid #eee;
}

.loading-state {
  text-align: center;
  padding: 3rem 1rem;
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
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: #fef3f2;
  border-bottom: 1px solid #fecdca;
  padding: 1rem 0;
  z-index: 1100;
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
  .header-content {
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
  
  .modal-actions {
    flex-direction: column;
  }
  
  .modal-content {
    margin: 1rem;
    max-height: calc(100vh - 2rem);
  }
  
  .detail-group {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .detail-group label {
    margin-bottom: 0.25rem;
  }
  
  .error-content {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
}
</style>