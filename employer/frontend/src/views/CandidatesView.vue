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
        <!-- Сообщение об ошибке -->
        <div v-if="errorMessage" class="error-state">
            <p>🚫 Ошибка: {{ errorMessage }}</p>
        </div>

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
              <!-- Изменено: теперь используется внутренний <span> для стилизации только балла -->
              <p class="score-line">
                  <strong>Баллы за собеседование с ИИ:</strong>
                  <span :class="['score-badge', getScoreColorClass(candidate.interview_score)]">
                      {{ candidate.interview_score || 'Нет оценки' }}
                  </span>
              </p>
              <!-- Предполагаем, что бэкенд вернет эти данные в удобном формате -->
              <p><strong>Опыт работы:</strong> {{ candidate.experience || 'Не указан' }}</p>
              <p><strong>Желаемая зарплата:</strong> {{ candidate.salary_expectation || 'Не указаны' }}</p>
              <p><strong>Дата отклика:</strong> {{ formatDate(candidate.created_at) }}</p>
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
      candidates: [],      // Список кандидатов (теперь с полем interview_score)
      currentVacancy: null, // Данные текущей вакансии
      loading: false,       // Индикатор загрузки
      errorMessage: ''      // Текст ошибки
    }
  },
  methods: {
    // === ОСНОВНАЯ ЛОГИКА ЗАГРУЗКИ ===
    async loadCandidates() {
      this.loading = true
      this.errorMessage = ''
      
      try {
        const vacancyId = this.$route.params.vacancyId
        
        // 1. Загружаем данные самой вакансии (для заголовка и проверок)
        this.currentVacancy = await api.getVacancyById(vacancyId)
        
        // 2. Загружаем список кандидатов
        // Бэкенд теперь возвращает массив объектов, где есть поле interview_score (float или null)
        const response = await api.getCandidatesForVacancy(vacancyId)
        
        // Сохраняем в переменную данных
        this.candidates = response
        
        console.log('Кандидаты загружены:', this.candidates)

      } catch (error) {
        console.error('Ошибка при загрузке кандидатов:', error)
        this.errorMessage = this.getErrorMessage(error)
      } finally {
        this.loading = false
      }
    },

    // === ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ДЛЯ ШАБЛОНА ===

    // Получение класса цвета в зависимости от балла (теперь возвращает кастомные классы)
    getScoreColorClass(score) {
      const numScore = parseFloat(score)
      // Если оценка отсутствует или невалидна
      if (isNaN(numScore) || numScore === null || numScore === undefined) {
        return 'score-none' 
      }
      
      // Логика баллов
      if (numScore >= 4) return 'score-high' // 4 и выше
      if (numScore >= 2) return 'score-medium' // 2 или 3
      return 'score-low' // 0 или 1
    },

    // Получение текстового статуса
    getStatusText(status) {
      const statusMap = {
        new: 'Новый',
        reviewed: 'Просмотрен',
        interview_passed: 'Интервью пройдено',
        interview_failed: 'Интервью не пройдено',
        rejected: 'Отклонен',
        invited: 'Приглашен'
      }
      return statusMap[status] || status
    },

    // Класс для статуса
    getStatusClass(status) {
      const map = {
        new: 'bg-blue-100 text-blue-800', // Эти классы из вашей стилизации, но могут не работать без Tailwind
        interview_passed: 'bg-green-100 text-green-800',
        interview_failed: 'bg-red-100 text-red-800',
        rejected: 'bg-gray-100 text-gray-600',
      }
      // Возвращаем класс, который используется в секции <style> (candidate-status)
      return status
    },

    // Обработка ошибок
    getErrorMessage(error) {
      const message = error.message || 'Произошла ошибка'
      if (message.includes('401') || message.includes('authentication')) {
        return 'Ошибка авторизации. Пожалуйста, войдите снова.'
      } else if (message.includes('404')) {
        return 'Вакансия не найдена.'
      } else if (message.includes('403')) {
        return 'У вас нет прав на просмотр этой вакансии.'
      }
      return message
    },
    
    // Форматирование даты
    formatDate(dateString) {
      if (!dateString) return ''
      try {
        return new Date(dateString).toLocaleDateString('ru-RU')
      } catch {
        return dateString
      }
    },

    // Действия (заглушки)
    viewCandidateDetails(candidate) {
      console.log('Открыть кандидата:', candidate)
      // Логика перехода или открытия модалки
    },
    
    downloadResume(candidate) {
       if (candidate.resume_url) {
        const url = candidate.resume_url.startsWith('http') 
          ? candidate.resume_url 
          : `http://localhost:8000${candidate.resume_url}`
        window.open(url, '_blank')
      } else {
        alert("Ссылка на резюме не найдена")
      }
    }
  },

  mounted() {
    // Проверка авторизации при загрузке компонента
    if (!authUtils.isAuthenticated()) {
      this.$router.push('/login')
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

/* --- НОВЫЕ СТИЛИ ДЛЯ БАЛЛОВ --- */

.score-line {
    /* Чтобы балл и текст были на одной линии */
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 0.5rem 0 !important;
}

.score-badge {
    /* Базовые стили для всех бейджей оценок */
    display: inline-block;
    padding: 4px 8px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.9rem;
}

/* Высокий балл (4+) */
.score-badge.score-high {
    background-color: #d1fae5; /* Светло-зеленый фон */
    color: #065f46; /* Темно-зеленый текст */
    border: 1px solid #a7f3d0;
}

/* Средний балл (2-3) */
.score-badge.score-medium {
    background-color: #fffbeb; /* Светло-желтый фон */
    color: #b45309; /* Темно-оранжевый текст */
    border: 1px solid #fcd34d;
}

/* Низкий балл (0-1) */
.score-badge.score-low {
    background-color: #fee2e2; /* Светло-красный фон */
    color: #b91c1c; /* Темно-красный текст */
    border: 1px solid #fca5a5;
}

/* Нет оценки */
.score-badge.score-none {
    background-color: #f3f4f6; /* Серый фон */
    color: #6b7280; /* Серый текст */
    border: 1px solid #e5e7eb;
    font-weight: 500;
}

/* --- КОНЕЦ НОВЫХ СТИЛЕЙ --- */


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