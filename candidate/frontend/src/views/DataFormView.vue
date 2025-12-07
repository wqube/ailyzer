<template>
  <div class="data-form-view">
    <!-- Модальное окно с информацией о вакансии -->
    <VacancyDetailsModal
      :show="showVacancyModal"
      :vacancyData="vacancyData"
      :loading="loadingVacancy"
      :error="vacancyError"
      :getLevelText="getLevelText"
      @close="closeVacancyModal"
    />

    <!-- Кнопка для просмотра информации о вакансии (если есть) -->
    <VacancyInfoButton 
      :vacancyData="vacancyData"
      :showVacancyModal="showVacancyModal"
      @open-modal="openVacancyModal"
    />

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

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/utils/api'
import VacancyInfoButton from '../components/VacancyInfoButton.vue'
import VacancyDetailsModal from '../components/VacancyDetailsModal.vue'

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
/* Основные стили */

.data-form-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
}

.form-section {
  width: 100%;
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