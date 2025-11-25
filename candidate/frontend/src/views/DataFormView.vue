<template>
  <div class="data-form-view">
    <header class="header">
      <div class="container">
        <div class="logo">
          <h1>AIlyzer</h1>
        </div>
        <div class="header-actions">
          <span class="page-title">Заполнение профиля</span>
        </div>
      </div>
    </header>

    <main class="main-content">
      <section class="form-section">
        <div class="container">
          <!-- Информация о вакансии -->
          <div v-if="vacancyData" class="vacancy-info-card">
            <h3>📋 Отклик на вакансию</h3>
            <div class="vacancy-details">
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
          </div>

          <!-- Индикатор загрузки вакансии -->
          <div v-if="loadingVacancy" class="loading-card">
            <div class="loading-spinner"></div>
            <p>Загрузка информации о вакансии...</p>
          </div>

          <!-- Сообщение об ошибке -->
          <div v-if="vacancyError" class="error-card">
            <p>⚠️ {{ vacancyError }}</p>
            <p>Вы все еще можете заполнить форму для общего анализа резюме.</p>
          </div>

          <!-- Форма заполнения данных -->
          <div class="form-card">
            <h2>Заполните ваш профиль</h2>
            <p class="subtitle">
              {{ vacancyData 
                ? 'Заполните данные для отклика на вакансию' 
                : 'Эта информация поможет нам подобрать для вас подходящие вакансии' 
              }}
            </p>
            
            <form @submit.prevent="submitForm" class="profile-form">
              <div class="form-group">
                <label for="fullName">ФИО *</label>
                <input 
                  type="text" 
                  id="fullName" 
                  v-model="formData.fullName" 
                  placeholder="Иванов Иван Иванович" 
                  required
                >
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label for="email">Email *</label>
                  <input 
                    type="email" 
                    id="email" 
                    v-model="formData.email" 
                    placeholder="ivanov@example.com"
                    required
                  >
                </div>
                <div class="form-group">
                  <label for="phone">Телефон *</label>
                  <input 
                    type="tel" 
                    id="phone" 
                    v-model="formData.phone" 
                    placeholder="+7 (999) 999-99-99"
                    required
                  >
                </div>
              </div>
              
              <div class="form-actions">
                <button type="submit" class="btn btn-primary btn-full">
                  {{ vacancyData ? 'Продолжить к загрузке резюме' : 'Отправить' }}
                </button>
              </div>
            </form>
            
            <div class="next-step">
              <p>После заполнения профиля вы сможете загрузить резюме для анализа</p>
            </div>
          </div>
        </div>
      </section>
    </main>

    <footer class="footer">
      <div class="container">
        <p>&copy; 2025 AIlyzer. ARPL Team.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/utils/api'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const formData = ref({
  fullName: '',
  email: '',
  phone: '',
})

const vacancyData = ref(null)
const loadingVacancy = ref(false)
const vacancyError = ref('')

// Получение текста уровня вакансии
const getLevelText = (level) => {
  const levelMap = {
    junior: 'Junior',
    middle: 'Middle',
    senior: 'Senior',
    lead: 'Lead'
  }
  return levelMap[level] || level
}

// Загрузка данных вакансии
const loadVacancyData = async (vacancyId) => {
  loadingVacancy.value = true
  vacancyError.value = ''
  
  try {
    // ⚠️ ИСПРАВЛЕНИЕ: Используем api.getVacancy (как в обновленном api.js)
    const data = await api.getVacancyById(vacancyId)
    vacancyData.value = data
    
    // ⚠️ ИСПРАВЛЕНИЕ: Используем универсальный setUserData
    appStore.setUserData({
        vacancyId: parseInt(vacancyId),
        vacancyData: data
    })
    
    console.log('Vacancy data loaded:', data)
  } catch (error) {
    console.error('Error loading vacancy:', error)
    vacancyError.value = error.message || 'Не удалось загрузить данные вакансии'
    
    // Очищаем данные о вакансии, если произошла ошибка
    appStore.setUserData({
        vacancyId: null,
        vacancyData: null
    })
  } finally {
    loadingVacancy.value = false
  }
}

onMounted(async () => {
  appStore.loadFromStorage()
  
  // Загружаем существующие данные пользователя
  if (appStore.userData) {
    formData.value.fullName = appStore.userData.fullName || ''
    formData.value.email = appStore.userData.email || ''
    formData.value.phone = appStore.userData.phone || ''
  }
  
  // Проверяем наличие ID вакансии в URL
  const vacancyId = route.params.id
  if (vacancyId) {
    console.log('Vacancy ID from URL:', vacancyId)
    
    // Проверяем, есть ли данные вакансии в Store и соответствует ли ID
    const idInt = parseInt(vacancyId)
    const currentVacancyId = appStore.userData.vacancyId
    const currentVacancyData = appStore.userData.vacancyData
    
    if (currentVacancyId === idInt && currentVacancyData) {
        // Данные уже загружены, просто отображаем их
        vacancyData.value = currentVacancyData
        console.log('Vacancy data restored from store.')
    } else {
        // Загружаем данные с сервера
        await loadVacancyData(vacancyId)
    }
  } else {
    // Если ID вакансии в URL нет, очищаем данные о вакансии в store
    appStore.setUserData({ vacancyId: null, vacancyData: null })
    vacancyData.value = null
  }
})

const submitForm = () => {
  // Сохраняем контакты
  appStore.setResumeData({
    fullName: formData.value.fullName,
    email: formData.value.email,
    phone: formData.value.phone,
    resumeText: appStore.userData.resumeText ?? ''
  })

  // Определяем, куда переходить
  const vacancyId = route.params.id

  if (vacancyId) {
    // Если есть ID вакансии, переходим с ним
    router.push(`/resume-analysis/${vacancyId}`)
  } else {
    // Иначе обычный переход
    router.push('/resume-analysis')
  }
}
</script>

<style scoped>
.data-form-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
}

/* Карточка с информацией о вакансии */
.vacancy-info-card {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 2rem;
  border-radius: 10px;
  margin-bottom: 2rem;
  box-shadow: 0 10px 30px rgba(16, 185, 129, 0.2);
}

.vacancy-info-card h3 {
  margin: 0 0 1rem 0;
  font-size: 1.2rem;
  opacity: 0.9;
}

.vacancy-details h2 {
  margin: 0 0 1rem 0;
  font-size: 2rem;
  font-weight: 700;
}

.vacancy-level {
  margin: 0.5rem 0;
  font-size: 1.1rem;
}

.vacancy-description,
.vacancy-requirements {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.vacancy-description p,
.vacancy-requirements p {
  margin: 0.5rem 0;
  line-height: 1.6;
}

/* Индикатор загрузки */
.loading-card {
  background: white;
  padding: 3rem;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  text-align: center;
  margin-bottom: 2rem;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #10b981;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Карточка с ошибкой */
.error-card {
  background: #fee;
  border: 2px solid #fcc;
  color: #c33;
  padding: 1.5rem;
  border-radius: 10px;
  margin-bottom: 2rem;
  box-shadow: 0 4px 12px rgba(204, 51, 51, 0.1);
}

.error-card p {
  margin: 0.5rem 0;
  line-height: 1.6;
}

/* Основные стили */
.main-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
}

.form-section {
  width: 100%;
}

.container {
  max-width: 700px;
  margin: 0 auto;
  padding: 0 20px;
}

.form-card {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  width: 100%;
}

.form-card h2 {
  text-align: center;
  margin-bottom: 10px;
  color: #333;
  font-size: 2em;
}

.subtitle {
  text-align: center;
  margin-bottom: 30px;
  color: #666;
  font-size: 1.1em;
}

.profile-form .form-row {
  display: flex;
  gap: 15px;
}

.profile-form .form-group {
  margin-bottom: 20px;
  flex: 1;
}

.profile-form label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
  font-size: 1em;
}

.profile-form input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.profile-form input:focus {
  border-color: #10b981;
  outline: none;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}

.form-actions {
  margin-bottom: 20px;
}

.next-step {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  text-align: center;
}

.next-step p {
  margin-bottom: 15px;
  color: #666;
}

/* Header */
.header {
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 15px 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
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

/* Buttons */
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

.btn-primary:hover {
  background-color: #0da271;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

.btn-outline {
  background-color: transparent;
  color: #10b981;
  border: 1px solid #10b981;
}

.btn-outline:hover {
  background-color: #10b981;
  color: white;
}

.btn-full {
  width: 100%;
}

/* Footer */
.footer {
  background-color: #333;
  color: white;
  padding: 20px 0;
  text-align: center;
}

.footer p {
  margin: 0;
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
  
  .profile-form .form-row {
    flex-direction: column;
    gap: 0;
  }
  
  .form-card {
    padding: 30px 20px;
  }
  
  .form-card h2 {
    font-size: 1.5em;
  }

  .vacancy-info-card {
    padding: 1.5rem;
  }

  .vacancy-details h2 {
    font-size: 1.5rem;
  }
}
</style>