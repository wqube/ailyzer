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
        <!-- Список вакансий -->
        <div class="vacancies-list">
          <div 
            v-for="vacancy in vacancies" 
            :key="vacancy.id" 
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
            </div>
            
            <div class="vacancy-actions">
              <button 
                @click="editVacancy(vacancy)" 
                class="btn btn-outline"
              >
                Редактировать
              </button>
              <button 
                @click="deleteVacancy(vacancy.id)" 
                class="btn btn-danger"
              >
                Удалить
              </button>
            </div>
          </div>
        </div>

        <!-- Сообщение если вакансий нет -->
        <div v-if="vacancies.length === 0" class="empty-state">
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
            >
          </div>

          <div class="form-group">
            <label for="level">Уровень *</label>
            <select 
              id="level" 
              v-model="vacancyForm.level" 
              required
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
            ></textarea>
          </div>

          <div class="form-actions">
            <button 
              type="button" 
              @click="closeModal" 
              class="btn btn-outline"
            >
              Отмена
            </button>
            <button 
              type="submit" 
              :disabled="loading" 
              class="btn btn-primary"
            >
              {{ loading ? 'Сохранение...' : (editingVacancy ? 'Обновить' : 'Создать') }}
            </button>
          </div>
        </form>
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
      editingVacancy: null,
      vacancyForm: {
        title: '',
        level: 'middle',
        description: '',
        requirements: ''
      }
    }
  },
  computed: {
    // Тестовые данные для демонстрации
    testVacancies() {
      return [
        {
          id: 1,
          title: 'Frontend Developer (Vue.js)',
          level: 'middle',
          description: 'Разработка пользовательских интерфейсов для HR-платформы',
          requirements: 'Опыт работы с Vue.js 2+ года, знание JavaScript, HTML5, CSS3',
          status: 'active',
          created_at: '2024-01-15'
        },
        {
          id: 2,
          title: 'Backend Developer (Python)',
          level: 'senior',
          description: 'Разработка API и бизнес-логики платформы',
          requirements: 'Python 3+, FastAPI, PostgreSQL, опыт работы 3+ года',
          status: 'active',
          created_at: '2024-01-10'
        }
      ]
    }
  },
  methods: {
    // Загрузка вакансий
    async loadVacancies() {
      this.loading = true
      try {
        // TODO: Заменить на реальный API вызов
        // const response = await api.getMyVacancies()
        // this.vacancies = response
        
        // Временное использование тестовых данных
        this.vacancies = this.testVacancies
        
      } catch (error) {
        console.error('Error loading vacancies:', error)
        // В случае ошибки показываем тестовые данные
        this.vacancies = this.testVacancies
      } finally {
        this.loading = false
      }
    },

    // Создание/обновление вакансии
    async saveVacancy() {
      this.loading = true
      try {
        if (this.editingVacancy) {
          // TODO: Редактирование вакансии через API
          // await api.updateVacancy(this.editingVacancy.id, this.vacancyForm)
          console.log('Updating vacancy:', this.vacancyForm)
        } else {
          // TODO: Создание вакансии через API
          // const newVacancy = await api.createVacancy(this.vacancyForm)
          // this.vacancies.unshift(newVacancy)
          console.log('Creating vacancy:', this.vacancyForm)
          
          // Временное добавление в массив
          const newVacancy = {
            id: Date.now(),
            ...this.vacancyForm,
            status: 'active',
            created_at: new Date().toISOString()
          }
          this.vacancies.unshift(newVacancy)
        }
        
        this.closeModal()
        
      } catch (error) {
        console.error('Error saving vacancy:', error)
        alert('Ошибка при сохранении вакансии')
      } finally {
        this.loading = false
      }
    },

    // Редактирование вакансии
    editVacancy(vacancy) {
      this.editingVacancy = vacancy
      this.vacancyForm = { ...vacancy }
      this.showCreateForm = true
    },

    // Удаление вакансии
    async deleteVacancy(vacancyId) {
      if (!confirm('Вы уверены, что хотите удалить эту вакансию?')) {
        return
      }

      try {
        // TODO: Удаление через API
        // await api.deleteVacancy(vacancyId)
        
        this.vacancies = this.vacancies.filter(v => v.id !== vacancyId)
        
      } catch (error) {
        console.error('Error deleting vacancy:', error)
        alert('Ошибка при удалении вакансии')
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
    },

    // Вспомогательные методы
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
}
</style>