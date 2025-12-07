<template>
  <div v-if="show" class="modal-overlay">
    <div class="modal-content">
      <div class="modal-header">
        <h3>📋 Информация о вакансии</h3>
        <button class="modal-close" @click="$emit('close')">×</button>
      </div>
      <div class="modal-body">
        <div v-if="vacancyData" class="vacancy-details-modal">
          <h2>{{ vacancyData.title }}</h2>
          <p class="vacancy-level">
            <strong>Уровень:</strong> {{ getLevelText(vacancyData.level) }}
          </p>
          <div class="vacancy-description">
            <p><strong>Описание:</strong></p>
            <p>{{ vacancyData.description }}</p>
          </div>
          <div class="vacancy-requirements">
            <p><strong>Требования:</strong></p>
            <p>{{ vacancyData.requirements }}</p>
          </div>
        </div>

        <div v-if="loading" class="loading-modal">
          <div class="loading-spinner"></div>
          <p>Загрузка информации о вакансии...</p>
        </div>

        <div v-if="error" class="error-modal">
          <p>⚠️ {{ error }}</p>
          <p>Вы все еще можете продолжить работу.</p>
        </div>
      </div>
      <div class="modal-footer">
        <button @click="$emit('close')" class="btn btn-primary">Понятно</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  show: { // Соответствует showVacancyModal
    type: Boolean,
    required: true,
  },
  vacancyData: {
    type: [Object, null],
    default: null,
  },
  loading: { // Соответствует loadingVacancy
    type: Boolean,
    default: false,
  },
  error: { // Соответствует vacancyError
    type: String,
    default: '',
  },
  getLevelText: {
    type: Function,
    required: true,
  }
});

defineEmits(['close']);
</script>

<style scoped>
/* ======================================= */
/* ====== Стили модального окна ======= */
/* ======================================= */

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  animation: fadeIn 0.3s ease;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border-radius: 12px 12px 0 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3rem;
}

.modal-close {
  background: none;
  border: none;
  color: white;
  font-size: 28px;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.modal-close:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.modal-body {
  padding: 24px;
}

.vacancy-details-modal h2 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 1.8rem;
}

.vacancy-details-modal .vacancy-level {
  margin: 0 0 20px 0;
  font-size: 1.1rem;
  color: #555;
}

.vacancy-details-modal .vacancy-description,
.vacancy-details-modal .vacancy-requirements {
  margin-top: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #10b981;
}

.vacancy-details-modal .vacancy-description p,
.vacancy-details-modal .vacancy-requirements p {
  margin: 8px 0;
  line-height: 1.6;
  color: #555;
}

.loading-modal,
.error-modal {
  text-align: center;
  padding: 40px 20px;
}

.loading-modal .loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #10b981;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

.error-modal {
  color: #d32f2f;
}

.modal-footer {
  padding: 20px 24px;
  border-top: 1px solid #eee;
  text-align: right;
}

/* Анимации */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Адаптация */
@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    max-height: 85vh;
  }

  .modal-header {
    padding: 15px 20px;
  }

  .modal-body {
    padding: 20px;
  }

  .vacancy-details-modal h2 {
    font-size: 1.5rem;
  }
}

/* Общие стили для кнопок */
.btn {
  display: inline-block;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  text-decoration: none;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #10b981;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0da271;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>