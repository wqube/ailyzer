<template>
  <div class="vacancies-view">
    <div class="vacancies-header">
      <div class="container">
        <h1>Мои вакансии</h1>
        <button @click="showCreateForm = true" class="btn btn-primary">
          Создать вакансию
        </button>
      </div>
    </div>

    <div class="vacancies-content">
      <div class="container">
        <!-- Индикатор загрузки -->
        <div v-if="loading && vacancies.length === 0" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Загрузка вакансий...</p>
        </div>

        <!-- Список вакансий -->
        <div class="vacancies-list" v-else-if="vacancies.length > 0">
          <div 
            v-for="vacancy in vacancies" 
            :key="vacancy.vacancy_id || vacancy.id" 
            class="vacancy-card"
          >
            <div class="vacancy-header">
              <h3>{{ vacancy.title }}</h3>
              <span :class="['vacancy-status', vacancy.status]">
                {{ getStatusText(vacancy.status) }}
              </span>
            </div>
            
            <div class="vacancy-info">
              <p><strong>Уровень:</strong> {{ getLevelText(vacancy.level) }}</p>
              <p><strong>Описание:</strong> {{ vacancy.description }}</p>
              <p><strong>Требования:</strong> {{ vacancy.requirements }}</p>
              <p><strong>Создана:</strong> {{ formatDate(vacancy.created_at) }}</p>
              <p><strong>Ссылка для кандидатов:</strong></p>

              <div class="vacancy-link">
                <input 
                  :value="getVacancyPublicLink(vacancy)" 
                  readonly 
                  class="link-input"
                  ref="linkInput"
                >
                <button 
                  @click="copyVacancyLink(vacancy)" 
                  class="btn btn-outline btn-small"
                  :class="{ 'copied': copiedLinkId === (vacancy.vacancy_id || vacancy.id) }"
                >
                  {{ copiedLinkId === (vacancy.vacancy_id || vacancy.id) ? 'Скопировано!' : 'Копировать' }}
                </button>
              </div>
            </div>
            
            <div class="vacancy-actions">
              <button 
                @click="editVacancy(vacancy)" 
                class="btn btn-outline"
                :disabled="actionLoading"
              >
                Редактировать
              </button>
              <button 
                @click="deleteVacancy(vacancy)" 
                class="btn btn-danger"
                :disabled="actionLoading"
              >
                Удалить
              </button>
            </div>
          </div>
        </div>

        <!-- Сообщение если вакансий нет -->
        <div v-else class="empty-state">
          <div class="empty-icon">📋</div>
          <h3>У вас пока нет вакансий</h3>
          <p>Создайте первую вакансию чтобы начать поиск кандидатов</p>
          <button @click="showCreateForm = true" class="btn btn-primary">
            Создать первую вакансию
          </button>
        </div>
      </div>
    </div>

    <!-- Модальное окно создания/редактирования вакансии -->
    <div v-if="showCreateForm" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ editingVacancy ? 'Редактировать вакансию' : 'Создать вакансию' }}</h2>
          <button @click="closeModal" class="btn-close">&times;</button>
        </div>
        
        <form @submit.prevent="saveVacancy" class="vacancy-form">
          <div class="form-group">
            <label for="title">Название вакансии *</label>
            <input 
              type="text" 
              id="title" 
              v-model="vacancyForm.title" 
              required 
              placeholder="Например: Frontend Developer"
              :disabled="formLoading"
            >
          </div>

          <div class="form-group">
            <label for="level">Уровень *</label>
            <select 
              id="level" 
              v-model="vacancyForm.level" 
              required
              :disabled="formLoading"
            >
              <option value="junior">Junior</option>
              <option value="middle">Middle</option>
              <option value="senior">Senior</option>
              <option value="lead">Lead</option>
            </select>
          </div>

          <div class="form-group">
            <label for="description">Описание вакансии *</label>
            <textarea 
              id="description" 
              v-model="vacancyForm.description" 
              required 
              rows="4"
              placeholder="Опишите чем будет заниматься сотрудник..."
              :disabled="formLoading"
            ></textarea>
          </div>

          <div class="form-group">
            <label for="requirements">Требования *</label>
            <textarea 
              id="requirements" 
              v-model="vacancyForm.requirements" 
              required 
              rows="4"
              placeholder="Опишите требования к кандидату..."
              :disabled="formLoading"
            ></textarea>
          </div>

          <div class="form-actions">
            <button 
              type="button" 
              @click="closeModal" 
              class="btn btn-outline"
              :disabled="formLoading"
            >
              Отмена
            </button>
            <button 
              type="submit" 
              :disabled="formLoading" 
              class="btn btn-primary"
            >
              {{ formLoading ? 'Сохранение...' : (editingVacancy ? 'Обновить' : 'Создать') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Уведомления об ошибках -->
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
  name: 'VacanciesView',
  data() {
    return {
      vacancies: [],
      showCreateForm: false,
      loading: false,
      formLoading: false,
      actionLoading: false,
      errorMessage: '',
      copiedLinkId: null, // Для отслеживания скопированной ссылки
      editingVacancy: null,
      vacancyForm: {
        title: '',
        level: 'middle',
        description: '',
        requirements: ''
      }
    }
  },
  methods: {
    // Загрузка вакансий
    async loadVacancies() {
      this.loading = true
      this.errorMessage = ''
      
      try {
        const response = await api.getMyVacancies()
        this.vacancies = response
        
      } catch (error) {
        console.error('Error loading vacancies:', error)
        this.errorMessage = this.getErrorMessage(error)
        
        // Если ошибка авторизации - перенаправляем на логин
        if (error.message.includes('401') || error.message.includes('authentication')) {
          this.$router.push({ name: 'employer-login' })
        }
      } finally {
        this.loading = false
      }
    },

    // Создание/обновление вакансии
    async saveVacancy() {
      console.log('=== SAVE VACANCY CALLED ===')
      console.log('Editing vacancy:', this.editingVacancy)
      
      this.formLoading = true
      this.errorMessage = ''
      
      try {
        if (this.editingVacancy) {
          // ИСПРАВЛЕНО: используем vacancy_id вместо id
          const vacancyId = this.editingVacancy.vacancy_id || this.editingVacancy.id
          console.log('Vacancy ID for update:', vacancyId)
          
          const updatedVacancy = await api.updateVacancy(vacancyId, this.vacancyForm)
          console.log('Update response:', updatedVacancy)
          
          // Обновляем вакансию в списке - тоже исправляем ID
          const index = this.vacancies.findIndex(v => 
            (v.vacancy_id || v.id) === (this.editingVacancy.vacancy_id || this.editingVacancy.id)
          )
          if (index !== -1) {
            this.vacancies.splice(index, 1, updatedVacancy)
          }
        } else {
          // Создание новой вакансии
          const newVacancy = await api.createVacancy(this.vacancyForm)
          console.log('Create response:', newVacancy)
          this.vacancies.unshift(newVacancy)
        }
        
        this.closeModal()
        this.showSuccessMessage(this.editingVacancy ? 'Вакансия обновлена' : 'Вакансия создана')
        
      } catch (error) {
        console.error('Error saving vacancy:', error)
        this.errorMessage = this.getErrorMessage(error)
      } finally {
        this.formLoading = false
      }
    },

    // Редактирование вакансии
    editVacancy(vacancy) {
      console.log('=== EDIT VACANCY ===')
      console.log('Vacancy object:', vacancy)
      
      this.editingVacancy = vacancy
      this.vacancyForm = { 
        title: vacancy.title,
        level: vacancy.level,
        description: vacancy.description,
        requirements: vacancy.requirements
      }
      this.showCreateForm = true
    },

    // Удаление вакансии
    async deleteVacancy(vacancy) {
      console.log('=== DELETE VACANCY CALLED ===')
      console.log('Vacancy object:', vacancy)
      
      // ИСПРАВЛЕНО: получаем ID из объекта вакансии
      const vacancyId = vacancy.vacancy_id || vacancy.id
      console.log('Vacancy ID to delete:', vacancyId)
      
      if (!confirm('Вы уверены, что хотите удалить эту вакансию?')) {
        return
      }

      this.actionLoading = true
      this.errorMessage = ''
      
      try {
        await api.deleteVacancy(vacancyId)
        console.log('Delete successful')
        
        // ИСПРАВЛЕНО: фильтруем по правильному ID
        this.vacancies = this.vacancies.filter(v => 
          (v.vacancy_id || v.id) !== vacancyId
        )
        this.showSuccessMessage('Вакансия удалена')
        
      } catch (error) {
        console.error('Error deleting vacancy:', error)
        this.errorMessage = this.getErrorMessage(error)
      } finally {
        this.actionLoading = false
      }
    },
    
    // Копирование ссылки в буфер обмена
    async copyVacancyLink(vacancy) {
      const link = this.getVacancyPublicLink(vacancy)
      const vacancyId = vacancy.vacancy_id || vacancy.id
      
      try {
        await navigator.clipboard.writeText(link)
        this.copiedLinkId = vacancyId
        
        // Сбрасываем статус "Скопировано" через 2 секунды
        setTimeout(() => {
          this.copiedLinkId = null
        }, 2000)
        
      } catch (err) {
        // Fallback для старых браузеров
        const input = this.$refs.linkInput[this.vacancies.indexOf(vacancy)]
        input.select()
        document.execCommand('copy')
        this.copiedLinkId = vacancyId
        
        setTimeout(() => {
          this.copiedLinkId = null
        }, 2000)
      }
    },

    // Закрытие модального окна
    closeModal() {
      this.showCreateForm = false
      this.editingVacancy = null
      this.vacancyForm = {
        title: '',
        level: 'middle',
        description: '',
        requirements: ''
      }
      this.errorMessage = ''
    },

    // Показать успешное сообщение
    showSuccessMessage(message) {
      // Здесь можно добавить красивые уведомления
      console.log(message)
      // Или интегрировать с системой уведомлений, если есть
    },

    // Обработка ошибок
    getErrorMessage(error) {
      const message = error.message || 'Произошла ошибка'
      
      if (message.includes('401') || message.includes('authentication')) {
        return 'Ошибка авторизации. Пожалуйста, войдите снова.'
      } else if (message.includes('network') || message.includes('fetch')) {
        return 'Ошибка соединения. Проверьте подключение к интернету.'
      } else if (message.includes('500')) {
        return 'Внутренняя ошибка сервера. Попробуйте позже.'
      }
      
      return message
    },

    // Форматирование даты
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('ru-RU')
    },

    //////////////////////// Вспомогательные методы ////////////////////////
    getStatusText(status) {
      const statusMap = {
        active: 'Активна',
        closed: 'Закрыта',
        draft: 'Черновик'
      }
      return statusMap[status] || status
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

    //////////////////////// Генерация публичной ссылки на вакансию ////////////////////////
    getVacancyPublicLink(vacancy) {
      const vacancyId = vacancy.vacancy_id || vacancy.id
      return `${window.location.origin}/vacancy/${vacancyId}`
    },

    // Показ QR-кода для ссылки (опционально)
    showQRCode(vacancy) {
      const link = this.getVacancyPublicLink(vacancy)
      // Здесь можно интегрировать библиотеку для генерации QR-кода
      console.log('QR Code for:', link)
      // Или открыть модальное окно с QR-кодом
    }
  },

  mounted() {
    // Проверяем авторизацию
    if (!authUtils.isAuthenticated()) {
      this.$router.push({ name: 'employer-login' })
      return
    }
    
    this.loadVacancies()
  }
}
</script>

<style scoped>
.vacancies-view {
  min-height: 80vh;
}

.vacancies-header {
  background: white;
  padding: 2rem 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 2rem;
}

.vacancies-header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.vacancies-header h1 {
  color: #333;
  margin: 0;
}

.vacancies-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.vacancy-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #8B5FBF;
}

.vacancy-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.vacancy-header h3 {
  margin: 0;
  color: #333;
  flex: 1;
}

.vacancy-status {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.vacancy-status.active {
  background: #e7f7ef;
  color: #10b981;
}

.vacancy-status.closed {
  background: #fef3f2;
  color: #f04444;
}

.vacancy-info {
  margin-bottom: 1.5rem;
}

.vacancy-info p {
  margin: 0.5rem 0;
  color: #666;
}

.vacancy-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-danger {
  background: #f04444;
  color: white;
  border: none;
}

.btn-danger:hover {
  background: #d92d20;
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

.vacancy-form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

@media (max-width: 768px) {
  .vacancies-header .container {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .vacancy-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .vacancy-actions {
    flex-direction: column;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .modal-content {
    margin: 1rem;
    max-height: calc(100vh - 2rem);
  }
  /* Добавляем новые стили для индикаторов загрузки и ошибок */
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

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Адаптивность */
@media (max-width: 768px) {
  .error-content {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
    }
  }
}

.vacancy-link {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.link-input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #f9f9f9;
  font-size: 0.9rem;
  color: #666;
}

.btn-small {
  padding: 0.5rem 1rem;
  font-size: 0.8rem;
}

.btn.copied {
  background: #10b981;
  color: white;
  border-color: #10b981;
}

/* Адаптивность */
@media (max-width: 768px) {
  .vacancy-link {
    flex-direction: column;
  }
}
</style>
