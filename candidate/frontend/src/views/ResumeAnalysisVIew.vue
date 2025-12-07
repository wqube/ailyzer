<template>
  <div class="resume-analysis-view">

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
      <section class="resume-section">
        <div class="container">


          <div class="resume-card">
            <h2>Анализ вашего резюме</h2>
            <p class="subtitle">
              {{ vacancyData 
                ? 'Загрузите резюме для отклика на вакансию' 
                : 'Загрузите ваше резюме, и наш ИИ проанализирует его и предложит подходящие вакансии' 
              }}
            </p>
            
            <div class="upload-container">
              <div class="upload-area" 
                   :class="{ 'dragover': isDragover }"
                   @click="triggerFileInput"
                   @drop="handleDrop"
                   @dragover="handleDragOver"
                   @dragleave="handleDragLeave">
                <div class="upload-icon">📄</div>
                <h3>Перетащите файл сюда или нажмите для выбора</h3>
                <p>Поддерживаемые форматы: PDF, DOC, DOCX (максимальный размер: 5MB)</p>
                <input 
                  type="file" 
                  ref="fileInput"
                  accept=".pdf,.doc,.docx" 
                  hidden
                  @change="handleFileSelect"
                >
                <button class="btn btn-outline">Выбрать файл</button>
              </div>
              
              <div v-if="selectedFile" class="file-info">
                <div class="file-details">
                  <div class="file-icon">📄</div>
                  <div class="file-name">{{ selectedFile.name }}</div>
                  <button class="remove-file" @click="removeFile">×</button>
                </div>
              </div>
              
              <div class="analysis-features">
                <h3>Что анализирует наш ИИ:</h3>
                <div class="features-list">
                  <div class="feature-item">
                    <span class="feature-icon">🔍</span>
                    <span>Ключевые навыки и компетенции</span>
                  </div>
                  <div class="feature-item">
                    <span class="feature-icon">📊</span>
                    <span>Опыт работы и достижения</span>
                  </div>
                  <div class="feature-item">
                    <span class="feature-icon">🎯</span>
                    <span>Соответствие требованиям вакансий</span>
                  </div>
                  <div class="feature-item">
                    <span class="feature-icon">💡</span>
                    <span>Рекомендации по улучшению резюме</span>
                  </div>
                </div>
              </div>
              
              <div class="form-actions">
                <button 
                  type="button" 
                  class="btn btn-primary btn-full" 
                  :disabled="!selectedFile || isLoading || !vacancyData"
                  @click="analyzeResume"
                >
                  <span v-if="isLoading">Анализ...</span>
                  <span v-else>Проанализировать резюме</span>
                </button>
                <p v-if="!vacancyData && route.params.id" class="warning-text">
                  ⚠️ Ожидание загрузки данных вакансии...
                </p>
              </div>
            </div>
            
            <div class="analysis-result" v-if="analysisResult">
              <h3>Результат анализа:</h3>
              <div class="result-card" :class="{ 'success': analysisResult.accepted, 'failure': !analysisResult.accepted }">
                <div class="result-icon">
                  {{ analysisResult.accepted ? '✅' : '❌' }}
                </div>
                <div class="result-content">
                  <h4>{{ analysisResult.accepted ? 'Резюме прошло проверку!' : 'Резюме требует доработки' }}</h4>
                  <p class="score">Оценка: <strong>{{ analysisResult.score }}%</strong></p>
                  <p class="message">{{ analysisResult.message }}</p>
                  <div v-if="analysisResult.errors && analysisResult.errors.length" class="errors">
                    <h5>Рекомендации по улучшению:</h5>
                    <ul>
                      <li v-for="(error, index) in analysisResult.errors" :key="index">{{ error }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="analysisResult && analysisResult.accepted" class="interview-action">
              <button @click="startInterview" class="btn btn-primary btn-large">
                Начать собеседование с ИИ
              </button>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/utils/api' 
import VacancyInfoButton from '../components/VacancyInfoButton.vue'
import VacancyDetailsModal from '../components/VacancyDetailsModal.vue'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const fileInput = ref(null)
const selectedFile = ref(null)
const isDragover = ref(false)
const isLoading = ref(false)
const analysisResult = ref(null)
const vacancyData = ref(null)
const loadingVacancy = ref(false)
const vacancyError = ref('')
const showVacancyModal = ref(false)

const userData = computed(() => appStore.userData)

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

// Открытие модального окна
const openVacancyModal = () => {
  showVacancyModal.value = true
}

// Закрытие модального окна
const closeVacancyModal = () => {
  showVacancyModal.value = false
}


onMounted(async () => {
  // Загружаем данные из localStorage
  appStore.loadFromStorage()
  
  // Проверяем, что пользователь заполнил основные данные
  if (!userData.value.fullName) {
    const vacancyId = route.params.id
    if (vacancyId) {
      router.push(`/${vacancyId}`)
    } else {
      router.push('/')
    }
    return
  }

  // --- ЛОГИКА ЗАГРУЗКИ ВАКАНСИИ ---
  const vacancyId = route.params.id
  if (vacancyId) {
    const idInt = parseInt(vacancyId)
    console.log('Resume analysis for vacancy:', idInt)
    // 1. Устанавливаем vacancyId в store
    appStore.setUserData({ vacancyId: idInt })
    
    // 2. Загружаем данные вакансии, если они еще не загружены или ID изменился
    // ⚠️ ИСПРАВЛЕНИЕ: Используем api.getVacancyById, как в обновленном api.js
    if (!userData.value.vacancyData || userData.value.vacancyData.vacancy_id !== idInt) {
      try {
        console.log(`Fetching vacancy data for ID: ${idInt}`)
        // Имитация загрузки
        isLoading.value = true 
        
        const response = await api.getVacancyById(idInt) 
        vacancyData.value = response
        appStore.setUserData({ vacancyData: response }) // Сохраняем в store
        console.log('Successfully fetched and saved vacancy data:', vacancyData.value)
      } catch (error) {
        console.error('Error fetching vacancy data:', error)
        // ⚠️ ИСПРАВЛЕНИЕ: Используем alert() для уведомления пользователя об ошибке, так как здесь нет модального окна
        alert(`Ошибка загрузки данных вакансии: ${error.message}. Убедитесь, что ID (${vacancyId}) корректен.`)
        vacancyData.value = null
      } finally {
        isLoading.value = false
      }
    } else {
      // Загружаем данные вакансии из store (если они были сохранены)
      vacancyData.value = userData.value.vacancyData
      console.log('Loaded vacancy data from store:', vacancyData.value)
    }
  } else {
    // Если нет ID вакансии, очищаем данные о вакансии из состояния
    appStore.setUserData({ vacancyId: null, vacancyData: null })
    vacancyData.value = null
  }
  // --- КОНЕЦ ЛОГИКИ ЗАГРУЗКИ ВАКАНСИИ ---
})

const triggerFileInput = () => fileInput.value?.click()

const handleFileSelect = (e) => {
  selectedFile.value = e.target.files[0]
  analysisResult.value = null
}

const handleDrop = (event) => {
  event.preventDefault()
  selectedFile.value = event.dataTransfer.files[0]
  analysisResult.value = null
  isDragover.value = false
}

const handleDragOver = (e) => {
  e.preventDefault()
  isDragover.value = true
}

const handleDragLeave = () => {
  isDragover.value = false
}

const removeFile = () => {
  selectedFile.value = null
  analysisResult.value = null
}

const analyzeResume = async () => {
  if (!selectedFile.value || !userData.value.vacancyId || !vacancyData.value) {
    alert("Пожалуйста, выберите файл и убедитесь, что данные вакансии загружены.")
    return
  }

  isLoading.value = true
  analysisResult.value = null
  
  let parsedResumeText = "";
  let newApplicationId = null; 

  try {
    console.log('=== STARTING RESUME ANALYSIS ===')
    
    // 1. Загружаем и анализируем резюме (Получаем распарсенный текст)
    const formData = new FormData()
    formData.append('resume', selectedFile.value)
    formData.append('fullname', userData.value.fullName)
    formData.append('vacancy_id', userData.value.vacancyId) 
    formData.append('select_language', 'ru')

    console.log('Uploading resume for analysis...')
    const result = await api.uploadResume(formData)
    console.log('Analysis result:', result)

    // 2. Обрабатываем результат анализа
    parsedResumeText = 
      result.parsed_text
      || result.resume_text
      || result.details
      || "";

    analysisResult.value = {
      accepted: result.accepted || result.passed,
      score: result.score || 0,
      message: result.message || 'Результат анализа получен',
      errors: result.errors || []
    }

    // 3. Формируем подробный topic для интервью
    const fullTopic = (
      `Вакансия: ${vacancyData.value.title}. Уровень: ${vacancyData.value.level}. ` +
      `Требования: ${vacancyData.value.requirements}. Описание: ${vacancyData.value.description}`
    )
    
    // 4. СОХРАНЯЕМ КАНДИДАТА В БД (Получаем application_id)
    console.log('=== SAVING CANDIDATE TO DATABASE ===')
    
    const candidateData = new FormData()
    candidateData.append("email", userData.value.email)
    candidateData.append("full_name", userData.value.fullName)
    candidateData.append("phone", userData.value.phone)
    candidateData.append("parsed_text", parsedResumeText)

    // --- ИСПРАВЛЕНИЕ: Включаем данные из формы (опыт, зарплата) в metadata_json ---
    const userMetadata = {
        // Добавляем результаты анализа, полученные с бэкенда
        analysis_result: result, 
        // Добавляем данные, введенные пользователем в форме DataFormView.vue
        experience: userData.value.experience,
        // Используем snake_case для бэкенда
        salary_expectation: userData.value.salaryExpectation 
    };
    
    // Удаляем пустые/нулевые значения, чтобы не отправлять их, если они не заданы
    Object.keys(userMetadata).forEach(key => {
        const value = userMetadata[key];
        if (value === null || value === '' || value === undefined) {
            delete userMetadata[key];
        }
    });

    candidateData.append("metadata_json", JSON.stringify(userMetadata));
    // ----------------------------------------------------------------------------------

    candidateData.append("resume", selectedFile.value)
    candidateData.append("vacancy_id", userData.value.vacancyId)

    // ----------------------------------------------------
    // !!! УЛУЧШЕННОЕ ЛОГИРОВАНИЕ ОШИБОК !!!
    // ----------------------------------------------------
    try {
      console.log('Calling api.createCandidate...')
      const candidateResponse = await api.createCandidate(candidateData)
      
      // Проверяем, что ID корректно вернулся
      if (candidateResponse && candidateResponse.application_id) {
        newApplicationId = candidateResponse.application_id
        console.log('✅ Кандидат успешно сохранён:', candidateResponse)
        console.log(`Retrieved application_id: ${newApplicationId}`)
      } else {
        console.error('Сервер вернул ответ, но application_id отсутствует. Полный ответ:', candidateResponse);
        throw new Error("Сервер не вернул application_id.") 
      }
    } catch (e) {
      console.error('❌ Критическая ошибка сохранения кандидата:', e)
      console.error('Полная информация об ошибке:', JSON.stringify(e, Object.getOwnPropertyNames(e))); 
      
      const errorMessage = e.message || 'Неизвестная ошибка API';
      analysisResult.value.errors.push(`Критическая ошибка сохранения данных: ${errorMessage}`)
      
      alert(`Критическая ошибка сохранения данных кандидата: ${errorMessage}. Невозможно продолжить интервью.`)
      
      isLoading.value = false;
      return; 
    }
    // ----------------------------------------------------

    // 5. Сохраняем результат анализа и подготавливаем данные для интервью
    
    // Обновляем базовые контактные данные и текст резюме
    appStore.setResumeData({
      fullName: userData.value.fullName,
      email: userData.value.email,
      phone: userData.value.phone,
      // Включаем опыт и зарплату обратно в Store, если они были обновлены парсером 
      // (хотя в нашем случае они берутся из формы)
      experience: userData.value.experience, 
      salaryExpectation: userData.value.salaryExpectation,
      resumeText: parsedResumeText
    })
    
    appStore.setResumeAnalysis(result)
    
    // Подготовка данных для интервью, включая application_id
    appStore.prepareInterviewData({
      topic: fullTopic,
      resumeText: parsedResumeText,
      application_id: newApplicationId 
    })

    console.log('=== RESUME ANALYSIS COMPLETED ===')

  } catch (err) {
    console.error('❌ CRITICAL ERROR in analyzeResume:', err)
    
    analysisResult.value = {
      accepted: false,
      score: 0,
      message: 'Ошибка анализа резюме',
      errors: [`Произошла ошибка: ${err.message}`]
    }
  } finally {
    isLoading.value = false
  }
}

const backToForm = () => {
  if (vacancyData.value) {
    router.push(`/${vacancyData.value.vacancy_id}`)
  } else {
    router.push('/')
  }
}

const startInterview = () => {
  // Убедимся, что ID заявки был сохранен перед переходом
  if (!appStore.userData?.interviewData?.application_id) {
    alert("Ошибка: Не удалось получить ID заявки. Пожалуйста, убедитесь, что вы нажали 'Анализировать резюме' и не было критических ошибок, затем попробуйте снова.")
    return
  }
  router.push('/interview')
}
</script>

<style scoped>

/* Основные стили */
.resume-analysis-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
}

.resume-section {
  width: 100%;
}

.resume-card {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  width: 100%;
}

.resume-card h2 {
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

.upload-container {
  margin: 30px 0;
}

.upload-area {
  border: 2px dashed #10b981;
  border-radius: 10px;
  padding: 40px 20px;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
}

.upload-area:hover {
  background-color: rgba(16, 185, 129, 0.05);
}

.upload-area.dragover {
  background-color: rgba(16, 185, 129, 0.1);
  border-color: #0da271;
}

.upload-icon {
  font-size: 50px;
  margin-bottom: 15px;
}

.upload-area h3 {
  margin-bottom: 10px;
  color: #333;
}

.upload-area p {
  color: #666;
  margin-bottom: 20px;
}

.file-info {
  margin: 20px 0;
}

.file-details {
  display: flex;
  align-items: center;
  background-color: #f0f9ff;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #e0f2fe;
}

.file-icon {
  font-size: 24px;
  margin-right: 15px;
}

.file-name {
  flex: 1;
  font-weight: 500;
}

.remove-file {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.remove-file:hover {
  color: #f44336;
}

.analysis-features {
  margin: 30px 0;
}

.analysis-features h3 {
  margin-bottom: 15px;
  color: #333;
}

.features-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.feature-icon {
  font-size: 20px;
}

.form-actions {
  margin: 30px 0;
}

.analysis-result {
  margin-top: 30px;
}

.analysis-result h3 {
  margin-bottom: 20px;
  color: #333;
}

.result-card {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 25px;
  border-radius: 10px;
  border: 2px solid;
}

.result-card.success {
  border-color: #10b981;
  background: #f0fdf4;
}

.result-card.failure {
  border-color: #ef4444;
  background: #fef2f2;
}

.result-icon {
  font-size: 2em;
}

.result-content h4 {
  margin-bottom: 10px;
  color: #333;
}

.score {
  font-size: 1.1em;
  margin-bottom: 10px;
}

.message {
  margin-bottom: 15px;
  color: #555;
}

.errors h5 {
  margin-bottom: 10px;
  color: #333;
}

.errors ul {
  list-style-type: none;
  padding-left: 0;
}

.errors li {
  padding: 5px 0;
  color: #666;
  position: relative;
  padding-left: 20px;
}

.errors li:before {
  content: "•";
  color: #ef4444;
  position: absolute;
  left: 0;
}

.interview-action {
  margin-top: 30px;
  text-align: center;
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
  
  .features-list {
    grid-template-columns: 1fr;
  }
  
  .upload-area {
    padding: 20px 15px;
  }
  
  .resume-card {
    padding: 30px 20px;
  }
  
  .result-card {
    flex-direction: column;
    text-align: center;
  }

  .vacancy-banner {
    padding: 1.5rem;
  }

  .vacancy-banner h2 {
    font-size: 1.5rem;
  }
}
</style>