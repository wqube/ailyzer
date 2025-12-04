<template>
  <div class="data-form-view">
    <!-- Модальное окно с информацией о вакансии -->
    <div v-if="showVacancyModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>📋 Информация о вакансии</h3>
          <button class="modal-close" @click="closeVacancyModal">×</button>
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
          
          <div v-if="loadingVacancy" class="loading-modal">
            <div class="loading-spinner"></div>
            <p>Загрузка информации о вакансии...</p>
          </div>
          
          <div v-if="vacancyError" class="error-modal">
            <p>⚠️ {{ vacancyError }}</p>
            <p>Вы все еще можете заполнить форму для общего анализа резюме.</p>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeVacancyModal" class="btn btn-primary">Понятно</button>
        </div>
      </div>
    </div>

    <!-- Кнопка для просмотра информации о вакансии (если есть) -->
    <div v-if="vacancyData && !showVacancyModal" class="vacancy-button-container">
      <button @click="openVacancyModal" class="btn btn-outline vacancy-info-btn">
        📋 Просмотреть информацию о вакансии
      </button>
    </div>

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
          <!-- Убрали блок с информацией о вакансии из основного контента -->

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

              <!-- НОВЫЕ НЕОБЯЗАТЕЛЬНЫЕ ПОЛЯ -->
              <div class="form-row">
                <div class="form-group">
                  <label for="experience">Опыт работы (лет)</label>
                  <input 
                    type="number" 
                    id="experience" 
                    v-model="formData.experience" 
                    placeholder="Например, 5"
                    min="0"
                  >
                </div>
                <div class="form-group">
                  <label for="salaryExpectation">Желаемая зарплата (RUB)</label>
                  <input 
                    type="number" 
                    id="salaryExpectation" 
                    v-model="formData.salaryExpectation" 
                    placeholder="Например, 150000"
                    min="0"
                  >
                </div>
              </div>
              <!-- КОНЕЦ НОВЫХ ПОЛЕЙ -->
              
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

    <Footer>
    </Footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/utils/api'
import Footer from '../components/Footer.vue'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const formData = ref({
  fullName: '',
  email: '',
  phone: '',
  experience: null,
  salaryExpectation: null,
})

const vacancyData = ref(null)
const loadingVacancy = ref(false)
const vacancyError = ref('')
const showVacancyModal = ref(false) // Новое состояние для модального окна

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
    const data = await api.getVacancyById(vacancyId)
    vacancyData.value = data
    
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

// Открытие модального окна
const openVacancyModal = () => {
  showVacancyModal.value = true
}

// Закрытие модального окна
const closeVacancyModal = () => {
  showVacancyModal.value = false
}

onMounted(async () => {
  appStore.loadFromStorage()
  
  // Загружаем существующие данные пользователя/резюме
  const storedData = appStore.resumeData || appStore.userData

  if (storedData) {
    formData.value.fullName = storedData.fullName || ''
    formData.value.email = storedData.email || ''
    formData.value.phone = storedData.phone || ''
    formData.value.experience = storedData.experience || null
    formData.value.salaryExpectation = storedData.salaryExpectation || null
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
  // Сохраняем контакты и опциональные поля
  appStore.setResumeData({
    fullName: formData.value.fullName,
    email: formData.value.email,
    phone: formData.value.phone,
    experience: formData.value.experience ? parseInt(formData.value.experience) : null,
    salaryExpectation: formData.value.salaryExpectation ? parseInt(formData.value.salaryExpectation) : null,
    resumeText: appStore.userData.resumeText ?? ''
  })

  // Определяем, куда переходить
  const vacancyId = route.params.id

  if (vacancyId) {
    router.push(`/resume-analysis/${vacancyId}`)
  } else {
    router.push('/resume-analysis')
  }
}
</script>

<style scoped>
*{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Стили для кнопки просмотра вакансии */
.vacancy-button-container {
  position: fixed;
  top: 100px;
  right: 20px;
  z-index: 1000;
}

.vacancy-info-btn {
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

/* Модальное окно */
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

/* Основные стили */
.data-form-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
}

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
  .vacancy-button-container {
    position: static;
    margin: 20px auto;
    text-align: center;
  }
  
  .vacancy-info-btn {
    width: 100%;
    margin: 0 20px;
  }
  
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
}
</style>