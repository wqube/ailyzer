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
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>{{ authStatusMessage }}</p>
        </div>

        <!-- Список вакансий -->
        <div class="vacancies-list" v-else-if="vacancies.length > 0">
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
              <!-- Обновлено: теперь используем vacancy.id как основной ключ -->
              <p><strong>ID:</strong> {{ vacancy.id }}</p>
              <p><strong>Уровень:</strong> {{ getLevelText(vacancy.level) }}</p>
              <p><strong>Описание:</strong> {{ vacancy.description }}</p>
              <p><strong>Требования:</strong> {{ vacancy.requirements }}</p>
              <!-- Используем created_at, который теперь будет меткой времени Firestore -->
              <p><strong>Создана:</strong> {{ formatDate(vacancy.created_at) }}</p>
              <p><strong>Ссылка для кандидатов:</strong></p>

              <div class="vacancy-link">
                <input 
                  :value="getVacancyPublicLink(vacancy)" 
                  readonly 
                  class="link-input"
                  :ref="el => { if (el) linkInputs[vacancy.id] = el }"
                >
                <button 
                  @click="copyVacancyLink(vacancy)" 
                  class="btn btn-outline btn-small"
                  :class="{ 'copied': copiedLinkId === vacancy.id }"
                >
                  {{ copiedLinkId === vacancy.id ? 'Скопировано!' : 'Копировать' }}
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

              <button 
                @click="closeVacancy(vacancy)" 
                class="btn btn-secondary"
                :disabled="actionLoading || vacancy.status === 'closed'"
                :class="{ 'btn-primary': vacancy.status !== 'closed' }"
                >
              {{ vacancy.status === 'closed' ? 'Закрыта' : 'Закрыть' }}
              </button>

              <!-- КНОПКА ПОЛНОГО УДАЛЕНИЯ -->
              <button 
                @click="permanentlyDeleteVacancy(vacancy)" 
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

    <!-- УВЕДОМЛЕНИЕ ОБ ОТМЕНЕ УДАЛЕНИЯ -->
    <div v-if="showUndo" class="undo-notification">
      <div class="container undo-container">
        <span>
          Вакансия удалена. Вы можете отменить это действие в течение 
          <strong>{{ deletionTimer }}</strong> сек.
        </span>
        <button @click="undoDelete" class="btn btn-undo">
          Отменить
        </button>
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
// Импорты Firebase
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from 'firebase/auth';
import { 
  getFirestore, collection, onSnapshot, deleteDoc, doc, setDoc, updateDoc, 
  query, orderBy, serverTimestamp 
} from 'firebase/firestore';

// Глобальные переменные Canvas (предполагаем, что они доступны)
const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
const firebaseConfig = JSON.parse(typeof __firebase_config !== 'undefined' ? __firebase_config : '{}');
const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;

// Заменяем импорт, так как используем прямые вызовы Firestore
// import { api, authUtils } from '@/utils/api' 

export default {
  name: 'VacanciesView',
  data() {
    return {
      // Firebase State
      db: null,
      auth: null,
      userId: null,
      isAuthReady: false,
      unsubscribe: null, // Для хранения функции отписки от onSnapshot
      authStatusMessage: 'Инициализация...',
      
      // Vacancy State
      vacancies: [],
      showCreateForm: false,
      loading: true, // Устанавливаем в true до готовности аутентификации
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
      deletionTimer: 10,
      timerInterval: null,
      showUndo: false,
    }
  },
  methods: {
    /**
     * Возвращает ссылку на публичную коллекцию вакансий.
     */
    getVacanciesCollectionRef() {
      if (!this.db) throw new Error("Firestore не инициализирован.");
      // Путь: /artifacts/{appId}/public/data/vacancies
      return collection(this.db, `artifacts/${appId}/public/data/vacancies`);
    },

    /**
     * Инициализирует Firebase и настраивает аутентификацию.
     */
    async initializeFirebase() {
      try {
        if (!firebaseConfig || Object.keys(firebaseConfig).length === 0) {
          this.errorMessage = "Конфигурация Firebase отсутствует.";
          return;
        }
        
        const app = initializeApp(firebaseConfig);
        this.db = getFirestore(app);
        this.auth = getAuth(app);
        
        // Аутентификация
        if (initialAuthToken) {
            await signInWithCustomToken(this.auth, initialAuthToken);
        } else {
            await signInAnonymously(this.auth);
        }
        
        onAuthStateChanged(this.auth, (user) => {
            this.userId = user?.uid || null;
            this.isAuthReady = true;
            this.loading = false;
            if (user) {
                this.authStatusMessage = 'Загрузка данных...';
                this.setupRealTimeListener(); 
            } else {
                this.authStatusMessage = 'Не удалось аутентифицировать пользователя.';
                this.errorMessage = this.authStatusMessage;
            }
        });

      } catch (error) {
        this.errorMessage = `Ошибка инициализации Firebase: ${error.message}`;
        this.loading = false;
        this.isAuthReady = true;
      }
    },

    // === ЛОГИКА РЕАЛЬНОГО ВРЕМЕНИ (onSnapshot) ===

    /**
     * Настраивает слушатель реального времени для обновления списка вакансий.
     * Заменяет loadVacancies().
     */
    setupRealTimeListener() {
      if (!this.isAuthReady || !this.userId) return;

      const q = query(this.getVacanciesCollectionRef(), orderBy('created_at', 'desc'));

      // onSnapshot автоматически обновляет this.vacancies при ЛЮБОМ изменении в БД
      this.unsubscribe = onSnapshot(q, (snapshot) => {
        this.errorMessage = ''; 
        const vacanciesData = [];
        snapshot.forEach(doc => {
          // Создаем объект с ID документа
          vacanciesData.push({
            id: doc.id,
            ...doc.data()
          });
        });
        
        // Сортируем в памяти для надежности, хотя запрос уже сортирует
        vacanciesData.sort((a, b) => {
            const dateA = a.created_at?.toDate ? a.created_at.toDate().getTime() : 0;
            const dateB = b.created_at?.toDate ? b.created_at.toDate().getTime() : 0;
            return dateB - dateA; // Новые вакансии сверху
        });

        this.vacancies = vacanciesData;
        this.loading = false;
        this.authStatusMessage = '';

      }, (error) => {
        this.errorMessage = "Ошибка при получении обновлений вакансий: " + error.message;
        this.loading = false;
      });
    },

    // === ЛОГИКА CRUD (Теперь Firestore) ===
    
    // Создание/обновление вакансии
    async saveVacancy() {
      if (!this.isAuthReady || !this.userId) {
          this.errorMessage = "Не авторизован.";
          return;
      }

      this.formLoading = true;
      this.errorMessage = '';
      
      try {
        const dataToSave = {
          ...this.vacancyForm,
          // Убедимся, что status присутствует для новых вакансий
          status: this.editingVacancy ? this.editingVacancy.status : 'active',
          // Добавляем ID создателя для безопасности (хотя используем публичную коллекцию)
          creatorId: this.userId, 
        };

        if (this.editingVacancy) {
          const vacancyId = this.editingVacancy.id;
          
          await updateDoc(doc(this.getVacanciesCollectionRef(), vacancyId), dataToSave);
          
        } else {
          // Для новой вакансии
          await setDoc(doc(this.getVacanciesCollectionRef()), {
            ...dataToSave,
            created_at: serverTimestamp() // Метка времени создания
          });
        }
        
        // onSnapshot автоматически обновит this.vacancies
        this.closeModal();
        this.showSuccessMessage(this.editingVacancy ? 'Вакансия обновлена' : 'Вакансия создана');
        
      } catch (error) {
        console.error('Error saving vacancy:', error);
        this.errorMessage = this.getErrorMessage(error);
      } finally {
        this.formLoading = false;
      }
    },
    
    // Закрытие вакансии (изменение статуса на 'closed')
    async closeVacancy(vacancy) {
      if (!this.isAuthReady || !this.userId) return;
      const vacancyId = vacancy.id;
      
      if (vacancy.status === 'closed') {
        // Заменяем alert на console.log (в соответствии с инструкциями)
        console.log('Вакансия уже закрыта'); 
        return;
      }
      
      if (!window.confirm('Вы уверены, что хотите закрыть эту вакансию? Кандидаты больше не смогут на нее откликаться.')) {
        return;
      }

      this.actionLoading = true;
      this.errorMessage = '';
      
      try {
        await updateDoc(doc(this.getVacanciesCollectionRef(), vacancyId), {
          status: 'closed'
        });
        
        // onSnapshot автоматически обновит список
        this.showSuccessMessage('Вакансия закрыта');
        
      } catch (error) {
        console.error('Error closing vacancy:', error);
        this.errorMessage = this.getErrorMessage(error);
      } finally {
        this.actionLoading = false;
      }
    },


    // === ЛОГИКА УДАЛЕНИЯ И ВОССТАНОВЛЕНИЯ (Fix: Теперь использует onSnapshot) ===
    
    // Полное удаление вакансии (с возможностью отмены)
    permanentlyDeleteVacancy(vacancy) {
      const vacancyId = vacancy.id;
      
      // Заменяем confirm на window.confirm для совместимости
      if (!window.confirm('ВНИМАНИЕ! Вы уверены, что хотите удалить эту вакансию? У вас будет 10 секунд на отмену.')) {
        return;
      }

      // 1. Очищаем предыдущий таймер, если он был
      this.clearDeleteTimer();
      
      // 2. Сохраняем удаляемую вакансию.
      this.deletedVacancy = vacancy;

      // 3. *ВРЕМЕННО* удаляем из локального списка, чтобы обеспечить визуальный эффект до истечения таймера.
      const index = this.vacancies.findIndex(v => v.id === vacancyId);
      if (index !== -1) {
        this.vacancies.splice(index, 1);
      }

      // 4. Запускаем таймер и уведомление
      this.deletionTimer = 10;
      this.showUndo = true;
      this.timerInterval = setInterval(() => {
        this.deletionTimer -= 1;
        
        if (this.deletionTimer <= 0) {
          this.finalizeDelete();
        }
      }, 1000);
    },
    
    // Окончательное удаление (когда таймер истек) - ИСПОЛЬЗУЕМ deleteDoc
    async finalizeDelete() {
      console.log('Finalizing permanent delete...');
      
      this.clearDeleteTimer();
      this.actionLoading = true;
      
      if (!this.deletedVacancy) {
        this.actionLoading = false;
        return;
      }

      try {
        const vacancyId = this.deletedVacancy.id;
        // КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: Вызываем deleteDoc. onSnapshot позаботится об обновлении UI.
        await deleteDoc(doc(this.getVacanciesCollectionRef(), vacancyId));

        this.showSuccessMessage(`Вакансия "${this.deletedVacancy.title}" окончательно удалена.`);
      } catch (error) {
        console.error('Error finalizing deletion:', error);
        
        // В случае ошибки, возвращаем вакансию в локальный список, чтобы onSnapshot ее не удалил,
        // пока пользователь не перезагрузит/пока не сработает onSnapshot с актуальным состоянием.
        this.vacancies.push(this.deletedVacancy); 
        this.vacancies.sort((a, b) => {
            const dateA = a.created_at?.toDate ? a.created_at.toDate().getTime() : 0;
            const dateB = b.created_at?.toDate ? b.created_at.toDate().getTime() : 0;
            return dateB - dateA;
        });

        this.errorMessage = `Не удалось окончательно удалить вакансию. ${this.getErrorMessage(error)}`;
      } finally {
        this.deletedVacancy = null;
        this.actionLoading = false;
      }
    },
    
    // Отмена удаления (нажата кнопка)
    undoDelete() {
      if (!this.deletedVacancy) return;

      console.log('Undo delete action...');
      
      // 1. Очищаем таймер и уведомление
      this.clearDeleteTimer();
      
      // 2. Возвращаем вакансию в локальный список
      // Поскольку onSnapshot еще не сработал на удаление (потому что удаление еще не было выполнено),
      // она останется в БД и отобразится на фронтенде.
      this.vacancies.push(this.deletedVacancy);
      this.vacancies.sort((a, b) => {
          const dateA = a.created_at?.toDate ? a.created_at.toDate().getTime() : 0;
          const dateB = b.created_at?.toDate ? b.created_at.toDate().getTime() : 0;
          return dateB - dateA;
      });
      
      this.showSuccessMessage(`Удаление вакансии "${this.deletedVacancy.title}" отменено.`);
      
      // 3. Сбрасываем временные данные
      this.deletedVacancy = null;
    },

    // Очистка интервала таймера
    clearDeleteTimer() {
      if (this.timerInterval) {
        clearInterval(this.timerInterval);
        this.timerInterval = null;
      }
      this.showUndo = false;
    },

    // Копирование ссылки в буфер обмена
    async copyVacancyLink(vacancy) {
      const link = this.getVacancyPublicLink(vacancy);
      const vacancyId = vacancy.id; // Используем .id
      
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

    // Просмотр кандидатов
    viewCandidates(vacancy) {
      const vacancyId = vacancy.id; // Используем .id
      this.$router.push({ 
        name: 'employer-candidates', 
        params: { vacancyId: vacancyId } 
      });
    },

    // Показать успешное сообщение
    showSuccessMessage(message) {
      console.log(`УСПЕХ: ${message}`);
    },

    // Обработка ошибок
    getErrorMessage(error) {
      const message = error.message || 'Произошла ошибка';
      
      // Можно убрать специфическую обработку 401/500, так как мы используем Firestore
      if (message.includes('permission-denied') || message.includes('auth')) {
          return 'Ошибка доступа (permission-denied). Проверьте правила безопасности Firestore.';
      }
      
      return message;
    },

    // Форматирование даты
    formatDate(date) {
      if (!date) return '—';
      // Если это метка времени Firestore, преобразуем ее в объект Date
      const dateObj = date.toDate ? date.toDate() : new Date(date);
      return dateObj.toLocaleDateString('ru-RU');
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
      const vacancyId = vacancy.id; // Используем .id
      // Здесь вам нужно подставить ваш реальный публичный домен, 
      // но для примера используем заглушку
      return `http://localhost:3000/vacancies/${vacancyId}`; 
    },
  },

  mounted() {
    this.initializeFirebase();
    
    // Удаляем старую проверку, так как она заменяется на onAuthStateChanged
    // if (!authUtils.isAuthenticated()) {
    //   this.$router.push({ name: 'employer-login' })
    //   return
    // }
  },
  
  // Отписка от слушателя при уничтожении компонента
  beforeDestroy() {
    this.clearDeleteTimer();
    if (this.unsubscribe) {
        this.unsubscribe();
    }
  }
}
</script>

<style scoped>
.btn-secondary {
  background: #6c757d;
  color: white;
  border: none;
  cursor: not-allowed;
}

.btn-secondary:hover {
  background: #6c757d;
  transform: none;
  box-shadow: none;
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

.undo-notification {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #333;
  color: #fff;
  padding: 10px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  min-width: 400px;
  text-align: center;
}

.undo-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
}

.btn-undo {
    background-color: #ff9800;
    color: #333;
    border: none;
    padding: 8px 15px;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.2s;
}

.btn-undo:hover {
    background-color: #ffa726;
}

/* Общие стили уведомлений (взято из предыдущих контекстов) */
.error-notification {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background-color: #f44336;
    color: white;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    z-index: 1000;
    width: 80%;
    max-width: 600px;
}

.error-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.btn-close-small {
    background: none;
    border: none;
    color: white;
    font-size: 1.2rem;
    cursor: pointer;
    line-height: 1;
    margin-left: 10px;
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
</style>