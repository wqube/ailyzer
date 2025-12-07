<template>
  <div v-if="vacancyData && !showVacancyModal" class="vacancy-button-container">
    <button @click="$emit('open-modal')" class="btn btn-outline vacancy-info-btn">
      📋 Просмотреть информацию о вакансии
    </button>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

// Определяем пропсы для передачи данных о вакансии и состоянии модального окна
defineProps({
  vacancyData: {
    type: [Object, null],
    default: null,
  },
  showVacancyModal: {
    type: Boolean,
    default: false,
  },
});

// Определяем событие, которое будет вызываться при нажатии
defineEmits(['open-modal']);
</script>

<style scoped>
/* Контейнер кнопки вакансии */
.vacancy-button-container {
  /* Стили для фиксированного положения (взяты из DataFormView.vue) */
  position: fixed;
  top: 100px;
  right: 20px;
  z-index: 1000;
}

.vacancy-info-btn {
  /* Общие стили кнопки (btn) должны быть в глобальном/базовом CSS */
  background-color: rgba(16, 185, 129, 0.1);
  border: 2px solid #10b981;
  color: #10b981;
  font-weight: 600;
  padding: 10px 15px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.vacancy-info-btn:hover {
  background-color: #10b981;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.3);
}

/* Адаптация для мобильных устройств (взята из DataFormView.vue) */
@media (max-width: 768px) {
  .vacancy-button-container {
    position: static;
    margin: 20px auto;
    text-align: center;
    width: 100%; /* Устанавливаем ширину для центрирования */
  }
  
  .vacancy-info-btn {
    width: calc(100% - 40px); /* Занимает всю доступную ширину с отступами */
    margin: 0 20px; /* Центрируем */
  }
}
</style>