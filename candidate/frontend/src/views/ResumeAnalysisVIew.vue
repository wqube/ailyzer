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
          <div class="resume-card">
            <h2>Анализ вашего резюме</h2>
            <p class="subtitle">Загрузите ваше резюме, и наш ИИ проанализирует его и предложит подходящие вакансии</p>
            
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
                  :disabled="!selectedFile || isLoading"
                  @click="analyzeResume"
                >
                  <span v-if="isLoading">Анализ...</span>
                  <span v-else>Проанализировать резюме</span>
                </button>
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
import { useRouter } from 'vue-router'
import { api } from '@/utils/api'

const router = useRouter()
const appStore = useAppStore()

const fileInput = ref(null)
const selectedFile = ref(null)
const isDragover = ref(false)
const isLoading = ref(false)
const analysisResult = ref(null)

const userData = computed(() => appStore.userData)

onMounted(() => {
  appStore.loadFromStorage()
  if (!userData.value.fullName) {
    router.push('/')
  }
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

const analyzeResume = async () => {
  if (!selectedFile.value) return

  isLoading.value = true
  analysisResult.value = null

  try {
    const formData = new FormData()
    formData.append('resume', selectedFile.value)
    formData.append('fullname', userData.value.fullName)
    formData.append('interview_topic', 'software_developer')
    formData.append('select_language', 'ru')

    const result = await api.uploadResume(formData)

    // Вывод данных анализа
    analysisResult.value = {
      accepted: result.accepted || result.passed,
      score: result.score || 0,
      message: result.message || 'Результат анализа получен',
      errors: result.errors || []
    }

    // ====== ВАЖНО: Сохранение данных в store ======

    // 1) Сохраняем текст резюме и основные данные
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


    // 2) Сохраняем результат анализа
    appStore.setResumeAnalysis(result)

// ============ СОХРАНЯЕМ КАНДИДАТА В БД ============

const candidateData = new FormData()
candidateData.append("email", userData.value.email)
candidateData.append("password_hash", "TEMP_PASSWORD_HASH")
candidateData.append("parsed_text", result.resume_text || result.details || "")
candidateData.append("metadata_json", JSON.stringify(result))
candidateData.append("resume", selectedFile.value)

try {
  const candidateResponse = await api.createCandidate(candidateData)
  console.log("Кандидат сохранён:", candidateResponse)
} catch (e) {
  console.error("Ошибка сохранения кандидата:", e)
}

    

    // 3) Формируем interviewData — БЕЗ ЭТОГО InterviewView НЕ ЗАПУСКАЕТСЯ
    appStore.prepareInterviewData()

    // ================================================

  } catch (err) {
    console.error(err)
    analysisResult.value = {
      accepted: false,
      score: 0,
      message: 'Ошибка анализа резюме',
      errors: ['Произошла ошибка. Попробуйте снова.']
    }
  }

  isLoading.value = false
}

const backToForm = () => router.push('/')

const startInterview = () => {
  // interviewData уже создано в analyzeResume
  router.push('/interview')
}
</script>



























































































<style scoped>
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

.resume-card {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 700px;
  margin: 0 auto;
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
}

.logo h1 {
  color: #10b981;
  font-size: 28px;
  font-weight: 700;
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
    margin: 20px;
  }
  
  .result-card {
    flex-direction: column;
    text-align: center;
  }
}
</style>