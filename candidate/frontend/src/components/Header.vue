<template>
  <header class="header">
    <div class="container">
      <div class="logo">
        <h1>Ailyzer</h1>
      </div>
      <div class="header-actions">
        <span class="page-title">{{ pageTitle }}</span>
        <button 
          v-if="showBackButton" 
          @click="handleBack" 
          class="btn btn-outline"
        >
          Назад
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// Определяем заголовок страницы на основе текущего маршрута
const pageTitle = computed(() => {
  switch (route.name) {
    case 'data-form':
    case 'data-form-vacancy':
      return 'Заполнение профиля'
    case 'resume-analysis':
    case 'resume-analysis-vacancy':
      return 'Анализ резюме'
    case 'interview':
      return 'Техническое собеседование'
    default:
      return 'AIlyzer'
  }
})

// Показывать кнопку "Назад" на страницах анализа и интервью
const showBackButton = computed(() => {
  return route.name === 'resume-analysis' || 
         route.name === 'resume-analysis-vacancy' || 
         route.name === 'interview'
})

// Обработчик кнопки "Назад"
const handleBack = () => {
  if (route.name === 'interview') {
    // Если на странице интервью - возвращаем на анализ резюме
    const vacancyId = route.params.id
    if (vacancyId) {
      router.push(`/resume-analysis/${vacancyId}`)
    } else {
      router.push('/resume-analysis')
    }
  } else if (route.name === 'resume-analysis' || route.name === 'resume-analysis-vacancy') {
    // Если на странице анализа - возвращаем на форму
    const vacancyId = route.params.id
    if (vacancyId) {
      router.push(`/${vacancyId}`)
    } else {
      router.push('/')
    }
  }
}
</script>

<style scoped>
.header {
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 15px 0; /* padding 0, чтобы фон доходил до края */
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo h1 {
  color: #10b981;
  font-size: 28px;
  font-weight: 700;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.page-title {
  font-weight: 500;
  color: #666;
}

.header .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

@media (max-width: 768px) {
  .header .container {
    flex-direction: column;
    gap: 15px;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 10px;
  }
}
</style>