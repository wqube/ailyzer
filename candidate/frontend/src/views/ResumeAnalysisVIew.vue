<template>
  <div class="resume-analysis-view">
    <header class="header">
      <div class="container">
        <div class="logo">
          <h1>AIlyzer</h1>
        </div>
        <div class="header-actions">
          <span class="page-title">Анализ резюме</span>
          <div class="auth-buttons">
            <button @click="backToForm" class="btn btn-outline">Назад</button>
          </div>
        </div>
      </div>
    </header>

    <main class="main-content">
      <section class="resume-section">
        <div class="container">
          <div v-if="vacancyData" class="vacancy-banner">
            <h3>📋 Отклик на вакансию</h3>
            <h2>{{ vacancyData.title }}</h2>
            <p class="vacancy-level">{{ getLevelText(vacancyData.level) }}</p>
          </div>

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

    <footer class="footer">
      <div class="container">
        <p>&copy; 2025 AIlyzer. ARPL Team.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/utils/api' // Предполагается, что api.getVacancy существует

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const fileInput = ref(null)
const selectedFile = ref(null)
const isDragover = ref(false)
const isLoading = ref(false)
const analysisResult = ref(null)
const vacancyData = ref(null)

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
    if (!userData.value.vacancyData || userData.value.vacancyData.vacancy_id !== idInt) {
      try {
        console.log(`Fetching vacancy data for ID: ${idInt}`)
        // Имитация загрузки
        isLoading.value = true 
        
        const response = await api.getVacancy(idInt) 
        vacancyData.value = response
        appStore.setUserData({ vacancyData: response }) // Сохраняем в store
        console.log('Successfully fetched and saved vacancy data:', vacancyData.value)
      } catch (error) {
        console.error('Error fetching vacancy data:', error)
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

  try {
    console.log('=== STARTING RESUME ANALYSIS ===')
    
    // 1. Загружаем и анализируем резюме
    const formData = new FormData()
    formData.append('resume', selectedFile.value)
    formData.append('fullname', userData.value.fullName)
    
    // !!! КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: Отправляем vacancy_id вместо interview_topic
    formData.append('vacancy_id', userData.value.vacancyId) 
    
    formData.append('select_language', 'ru')

    console.log('Uploading resume for analysis...')
    const result = await api.uploadResume(formData)
    console.log('Analysis result:', result)

    // 2. Обрабатываем результат анализа
    analysisResult.value = {
      accepted: result.accepted || result.passed,
      score: result.score || 0,
      message: result.message || 'Результат анализа получен',
      errors: result.errors || []
    }

    // 3. Формируем подробный topic для интервью и сохраняем данные в store
    const fullTopic = (
      `Вакансия: ${vacancyData.value.title}. Уровень: ${vacancyData.value.level}. ` +
      `Требования: ${vacancyData.value.requirements}. Описание: ${vacancyData.value.description}`
    )
    
    appStore.setResumeData({
      fullName: userData.value.fullName,
      email: userData.value.email,
      phone: userData.value.phone,
      resumeText: 
        result.parsed_text
        || result.resume_text
        || result.details
        || ""
    })
    
    // 4. Сохраняем результат анализа и данные для интервью
    appStore.setResumeAnalysis(result)
    
    // Подготовка данных для интервью с полным текстом вакансии в качестве темы
    appStore.prepareInterviewData({
      topic: fullTopic,
      resumeText: result.parsed_text || result.resume_text || result.details || ""
    })

    // 5. СОХРАНЯЕМ КАНДИДАТА В БД 
    console.log('=== SAVING CANDIDATE TO DATABASE ===')
    
    const candidateData = new FormData()
    candidateData.append("email", userData.value.email)
    candidateData.append("full_name", userData.value.fullName)
    candidateData.append("phone", userData.value.phone)
    candidateData.append("parsed_text", result.parsed_text || result.resume_text || result.details || "")
    candidateData.append("metadata_json", JSON.stringify(result))
    candidateData.append("resume", selectedFile.value)
    candidateData.append("vacancy_id", userData.value.vacancyId)

    try {
      console.log('Calling api.createCandidate...')
      const candidateResponse = await api.createCandidate(candidateData)
      console.log('✅ Кандидат успешно сохранён:', candidateResponse)
    } catch (e) {
      console.error('❌ Ошибка сохранения кандидата:', e)
      // В реальном приложении здесь нужна более изящная обработка ошибок
    }

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
  router.push('/interview')
}

</script>

<style scoped>
/* Баннер с информацией о вакансии */
.vacancy-banner {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 2rem;
  border-radius: 10px;
  margin-bottom: 2rem;
  text-align: center;
  box-shadow: 0 10px 30px rgba(16, 185, 129, 0.2);
}

.vacancy-banner h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  opacity: 0.9;
}

.vacancy-banner h2 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 700;
}

.vacancy-level {
  margin: 0;
  font-size: 1.2rem;
  opacity: 0.9;
}

/* Основные стили */
.resume-analysis-view {
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

.resume-section {
  width: 100%;
}

.container {
  max-width: 700px;
  margin: 0 auto;
  padding: 0 20px;
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

.btn-large {
  padding: 15px 40px;
  font-size: 1.1em;
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

.auth-buttons {
  display: flex;
  gap: 10px;
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

.btn-primary:hover:not(:disabled) {
  background-color: #0da271;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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