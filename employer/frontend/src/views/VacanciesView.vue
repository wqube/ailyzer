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

    <!-- УВЕДОМЛЕНИЕ ОБ ОТМЕНЕ УДАЛЕНИЯ (Закреплено сверху по центру) -->
    <div v-if="showUndo" class="undo-notification fixed-top-center">
      <div class="undo-content">
        <!-- Компактный текст и обратный отсчет -->
        <span class="timer-text">
          Удаление вакансии "{{ deletedVacancy?.title }}" через 
          <strong class="timer-countdown">{{ deletionTimer }}</strong> с.
        </span>
        <button @click="undoDelete" class="btn btn-undo">
          Отменить
        </button>
      </div>
    </div>
    <!-- КОНЕЦ УВЕДОМЛЕНИЯ -->

    <div class="vacancies-content">
      <div class="container">
        <!-- Индикатор загрузки -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Загрузка данных...</p>
        </div>

        <!-- Список вакансий -->
        <div class="vacancies-list" v-else-if="vacancies.length > 0">
          <div 
            v-for="vacancy in vacancies" 
            :key="vacancy.vacancy_id" 
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
                  :ref="el => { if (el) linkInputs[vacancy.vacancy_id] = el }"
                >
                <button 
                  @click="copyVacancyLink(vacancy)" 
                  class="btn btn-outline btn-small"
                  :class="{ 'copied': copiedLinkId === vacancy.vacancy_id }"
                >
                  {{ copiedLinkId === vacancy.vacancy_id ? 'Скопировано!' : 'Копировать' }}
                </button>
              </div>
            </div>
            
            <div class="vacancy-actions">
              <button 
                @click="viewCandidates(vacancy)" 
                class="btn btn-outline"
                :disabled="actionLoading"
                >
                Просмотр кандидатов
              </button>

              <button 
                @click="editVacancy(vacancy)" 
                class="btn btn-outline"
                :disabled="actionLoading || vacancy.status === 'closed'"
              >
                Редактировать
              </button>

              <!-- ОБНОВЛЕННАЯ КНОПКА ОТКРЫТЬ/ЗАКРЫТЬ -->
              <button 
                @click="vacancy.status === 'closed' ? openVacancy(vacancy) : closeVacancy(vacancy)" 
                :class="['btn', vacancy.status === 'closed' ? 'btn-primary' : 'btn-secondary']"
                :disabled="actionLoading"
              >
                {{ vacancy.status === 'closed' ? 'Открыть' : 'Закрыть' }}
              </button>
              <!-- КОНЕЦ ОБНОВЛЕННОЙ КНОПКИ -->

              <button 
                @click="triggerDeleteConfirmation(vacancy)" 
                class="btn btn-danger btn-small delete-btn"
                :disabled="actionLoading"
                title="Полное удаление вакансии из базы данных"
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
import { api } from '@/utils/api'; 

export default {
  name: 'VacanciesView',
  data() {
    return {
      // Data State
      vacancies: [],
      loading: true, 
      
      // UI State
      showCreateForm: false,
      formLoading: false,
      actionLoading: false, 
      errorMessage: '',
      copiedLinkId: null, 
      editingVacancy: null,
      vacancyForm: {
        title: '',
        level: 'middle',
        description: '',
        requirements: ''
      },
      linkInputs: {},

      // Логика отмены удаления 
      deletedVacancy: null, 
      deletionTimer: 5,  
      timerInterval: null, 
      showUndo: false,     
    }
  },
  methods: {
    // === API-ВЫЗОВЫ ===
    
    /**
     * Загружает вакансии с бэкенда
     */
    async fetchVacancies() {
      this.loading = true;
      this.errorMessage = '';
      try {
        const data = await api.getMyVacancies();
        // Сортируем полученные данные (новые сверху)
        this.vacancies = data.sort((a, b) => {
            return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        });
      } catch (error) {
        this.errorMessage = error.message || 'Ошибка загрузки вакансий с сервера.';
        console.error("Error fetching vacancies:", error);
        this.vacancies = []; 
      } finally {
        this.loading = false;
      }
    },
    
    // Создание/обновление вакансии
    async saveVacancy() {
      this.formLoading = true;
      this.errorMessage = '';
      
      try {
        if (this.editingVacancy) {
          await api.updateVacancy(this.editingVacancy.vacancy_id, this.vacancyForm);
          this.showSuccessMessage('Вакансия обновлена');
        } else {
          await api.createVacancy(this.vacancyForm); 
          this.showSuccessMessage('Вакансия создана');
        }
        
        this.closeModal();
        
      } catch (error) {
        console.error('Error saving vacancy:', error);
        this.errorMessage = error.message || 'Не удалось сохранить вакансию.';
      } finally {
        this.formLoading = false;
        await this.fetchVacancies(); 
      }
    },
    
    /**
     * Закрытие вакансии (изменение статуса на 'closed')
     */
    async closeVacancy(vacancy) {
      if (vacancy.status === 'closed') return;
      
      if (!window.confirm('Вы уверены, что хотите закрыть эту вакансию? Кандидаты больше не смогут откликаться.')) {
        return;
      }

      this.actionLoading = true;
      this.errorMessage = '';
      try {
        await api.updateVacancy(vacancy.vacancy_id, { status: 'closed' });
        this.showSuccessMessage('Вакансия закрыта');
      } catch (error) {
        this.errorMessage = error.message || 'Ошибка при закрытии вакансии.';
        console.error('Error closing vacancy:', error);
      } finally {
        this.actionLoading = false;
        await this.fetchVacancies();
      }
    },
    
    /**
     * Открытие вакансии (изменение статуса на 'active')
     */
    async openVacancy(vacancy) {
      if (vacancy.status === 'active') return;
      
      if (!window.confirm('Вы уверены, что хотите снова открыть эту вакансию? Кандидаты смогут продолжить откликаться.')) {
        return;
      }

      this.actionLoading = true;
      this.errorMessage = '';
      try {
        await api.updateVacancy(vacancy.vacancy_id, { status: 'active' });
        this.showSuccessMessage('Вакансия открыта и снова активна');
      } catch (error) {
        this.errorMessage = error.message || 'Ошибка при открытии вакансии.';
        console.error('Error opening vacancy:', error);
      } finally {
        this.actionLoading = false;
        await this.fetchVacancies();
      }
    },


    // === ЛОГИКА УДАЛЕНИЯ С ТАЙМЕРОМ ===
    
    /**
     * Запускает подтверждение удаления с таймером
     */
    triggerDeleteConfirmation(vacancy) {
      if (!window.confirm(`Вы уверены, что хотите безвозвратно удалить вакансию "${vacancy.title}"? У вас будет 5 секунд на отмену.`)) {
        return;
      }
      
      this.clearDeleteTimer();
      
      this.deletedVacancy = vacancy;
      this.showUndo = true;
      this.deletionTimer = 5; // Сброс до 5 секунд
      this.actionLoading = true; // Блокируем другие действия
      
      this.startDeletionTimer();
    },

    /**
     * Управляет обратным отсчетом
     */
    startDeletionTimer() {
      this.timerInterval = setInterval(() => {
        this.deletionTimer--;
        
        if (this.deletionTimer <= 0) {
          this.clearDeleteTimer();
          this.executePermanentDelete();
        }
      }, 1000);
    },

    /**
     * Выполняет API-вызов для безвозвратного удаления (конечный шаг)
     */
    async executePermanentDelete() {
      if (!this.deletedVacancy) return;

      this.errorMessage = '';
      const vacancyToDelete = this.deletedVacancy;
      
      // Сброс UI перед API-вызовом
      this.deletedVacancy = null;
      this.showUndo = false;
      this.actionLoading = false; 

      try {
        await api.deleteVacancy(vacancyToDelete.vacancy_id);
        this.showSuccessMessage(`Вакансия "${vacancyToDelete.title}" удалена.`);
      } catch (error) {
        this.errorMessage = error.message || 'Не удалось удалить вакансию с сервера.';
        console.error('Error executing permanent delete:', error);
      } finally {
        await this.fetchVacancies(); 
      }
    },

    /**
     * Отменяет удаление и сбрасывает состояние
     */
    undoDelete() {
        this.clearDeleteTimer();
        this.deletedVacancy = null;
        this.showUndo = false;
        this.actionLoading = false; 
        this.showSuccessMessage(`Удаление вакансии отменено.`);
    },
    
    /**
     * Утилита для очистки интервала таймера
     */
    clearDeleteTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    },
    
    // === КОНЕЦ ЛОГИКИ УДАЛЕНИЯ С ТАЙМЕРОМ ===

    // Редактирование вакансии
    editVacancy(vacancy) {
      if (vacancy.status === 'closed') return

      this.editingVacancy = { ...vacancy, vacancy_id: vacancy.vacancy_id }

      this.vacancyForm = { 
        title: vacancy.title,
        level: vacancy.level,
        description: vacancy.description,
        requirements: vacancy.requirements
      }
      this.showCreateForm = true
    },

    // Копирование ссылки в буфер обмена
    async copyVacancyLink(vacancy) {
      const link = this.getVacancyPublicLink(vacancy);
      const vacancyId = vacancy.vacancy_id; 
      
      try {
        await navigator.clipboard.writeText(link);
        this.copiedLinkId = vacancyId;
        
        setTimeout(() => {
          this.copiedLinkId = null;
        }, 2000);
        
      } catch (err) {
        const input = this.linkInputs[vacancyId];
        if (input) {
            input.select();
            document.execCommand('copy');
            this.copiedLinkId = vacancyId;
            
            setTimeout(() => {
              this.copiedLinkId = null;
            }, 2000);
        }
      }
    },

    // Закрытие модального окна
    closeModal() {
      this.showCreateForm = false;
      this.editingVacancy = null;
      this.vacancyForm = {
        title: '',
        level: 'middle',
        description: '',
        requirements: ''
      };
      this.errorMessage = '';
    },

    // Просмотр кандидатов (логика перенаправления)
    viewCandidates(vacancy) {
      const vacancyId = vacancy.vacancy_id; 
      
      if (this.$router) {
          this.$router.push({ 
              name: 'employer-candidates', 
              params: { 
                  vacancyId: vacancyId 
              } 
          });
      } else {
          console.error("Vue Router не доступен.");
      }
    },

    // Показать успешное сообщение (заглушка)
    showSuccessMessage(message) {
      console.log(`УСПЕХ: ${message}`);
    },

    // Форматирование даты
    formatDate(dateString) {
      if (!dateString) return '—';
      try {
        return new Date(dateString).toLocaleDateString('ru-RU');
      } catch (e) {
        return dateString; 
      }
    },

    //////////////////////// Вспомогательные методы ////////////////////////
    getStatusText(status) {
      const statusMap = {
        active: 'Активна',
        closed: 'Закрыта',
        draft: 'Черновик'
      };
      return statusMap[status] || status;
    },

    getLevelText(level) {
      const levelMap = {
        junior: 'Junior',
        middle: 'Middle', 
        senior: 'Senior',
        lead: 'Lead'
      };
      return levelMap[level] || level;
    },

    //////////////////////// Генерация публичной ссылки на вакансию ////////////////////////
    getVacancyPublicLink(vacancy) {
      const vacancyId = vacancy.vacancy_id; 
      return `http://localhost:3000/${vacancyId}`; 
    },
  },

  mounted() {
    this.fetchVacancies();
  },
  
  beforeUnmount() {
    this.clearDeleteTimer();
  }
}
</script>

<style scoped>
/* =================================
   СТАНДАРТНЫЕ СТИЛИ СТРАНИЦЫ
   ================================= */
.btn-secondary {
  background: #6c757d;
  color: white;
  border: none;
  /* УДАЛЕНО: cursor: not-allowed; - это была причина проблемы с видом "недоступно" */
}

.btn-secondary:hover {
  background: #5a6268; /* Добавлен hover-эффект для кликабельности */
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

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

/* Статусы вакансий */
.vacancy-status {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}
.vacancy-status.active {
  background-color: #e6ffed;
  color: #00873c;
}
.vacancy-status.closed {
  background-color: #fcebeb;
  color: #c90000;
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

/* Стили для ссылок и копирования */
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

/* Состояния */
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

/* Индикаторы загрузки */
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

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

/* Уведомления об ошибках */
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


/* =================================
   СТИЛИ УВЕДОМЛЕНИЯ ОБ ОТМЕНЕ (КОМПАКТНЫЙ)
   ================================= */
.fixed-top-center {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2000; 
  width: auto;
  max-width: 90%;
  animation: slideIn 0.3s ease-out;
}

.undo-notification {
  background-color: #333; 
  color: white;
  padding: 0.5rem 1rem; 
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  display: inline-block; 
}

.undo-content {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem; 
}

.timer-text {
  font-size: 0.9rem; 
  line-height: 1.5;
}

.timer-countdown {
  font-size: 1rem; 
  color: #FFC107; 
  font-weight: 700;
  margin-left: 5px;
}

.btn-undo {
  background-color: #4CAF50; 
  color: white;
  border: none;
  padding: 0.3rem 0.7rem; 
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  font-weight: bold;
  flex-shrink: 0; 
}

.btn-undo:hover {
  background-color: #45a049;
}

/* Анимация появления */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translate(-50%, -50px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}


/* =================================
   АДАПТИВНОСТЬ
   ================================= */
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

  .vacancy-link {
    flex-direction: column;
  }
  
  .error-content {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
}
</style>