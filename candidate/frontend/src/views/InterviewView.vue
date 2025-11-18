<template>
  <div class="interview-view">
    <header class="header">
      <div class="container">
        <div class="logo">
          <h1>AIlyzer</h1>
        </div>
        <div class="header-actions">
          <span class="page-title">Техническое собеседование</span>
          <button @click="backToAnalysis" class="btn btn-outline">Назад</button>
        </div>
      </div>
    </header>

    <main class="main-content">
      <section class="interview-section">
        <div class="container">
          <div class="interview-card">
            <div class="interview-header">
              <h2>Техническое собеседование с ИИ</h2>
              <p class="subtitle">Ответьте на вопросы нашего ИИ-интервьюера</p>
              
              <div class="interview-info">
                <div class="info-item">
                  <span class="label">Тема:</span>
                  <span class="value">{{ getTopicName(currentTopic) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Язык:</span>
                  <span class="value">{{ currentLanguage === 'ru' ? 'Русский' : 'Английский' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Вопрос:</span>
                  <span class="value">{{ currentQuestionNumber }}/{{ totalQuestions }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Текущий балл:</span>
                  <span class="value">{{ averageScore.toFixed(1) }}/5.0</span>
                </div>
              </div>
            </div>

            <div class="chat-container">
              <div class="messages-container" ref="messagesContainer">
                <div 
                  v-for="(message, index) in messages" 
                  :key="index"
                  :class="['message', message.type]"
                >
                  <div class="message-content">
                    <div class="message-sender">
                      {{ message.type === 'bot' ? '🤖 ИИ-Интервьюер' : '👤 Вы' }}
                    </div>
                    <div class="message-text">{{ message.text }}</div>
                    <div v-if="message.score !== undefined" class="message-score">
                      Оценка: <strong>{{ message.score }}/5</strong>
                      <span v-if="message.reasoning" class="reasoning">({{ message.reasoning }})</span>
                    </div>
                  </div>
                </div>
                
                <div v-if="isLoading" class="message bot">
                  <div class="message-content">
                    <div class="message-sender">🤖 ИИ-Интервьюер</div>
                    <div class="message-text typing">ИИ думает...</div>
                  </div>
                </div>
              </div>

              <div class="input-container" v-if="sessionId && !isFinished">
                <div class="input-group">
                  <textarea 
                    v-model="userAnswer" 
                    placeholder="Введите ваш ответ здесь..."
                    @keydown.enter.exact.prevent="sendAnswer"
                    :disabled="isLoading"
                    rows="3"
                  ></textarea>
                  <div class="input-actions">
                    <button 
                      @click="sendAnswer" 
                      :disabled="!userAnswer.trim() || isLoading"
                      class="btn btn-primary"
                    >
                      Отправить
                    </button>
                    <button 
                      v-if="isSpeechSupported"
                      @click="toggleVoiceInput"
                      :class="['btn', 'btn-outline', { 'listening': isListening }]"
                      :disabled="isLoading"
                    >
                      {{ isListening ? '🎤 Слушаю...' : '🎤 Голос' }}
                    </button>
                  </div>
                </div>
                <p class="hint">Нажмите Enter для отправки или используйте голосовой ввод</p>
              </div>

              <div v-if="!sessionId" class="start-section">
                <button 
                  @click="startInterview" 
                  :disabled="isLoading"
                  class="btn btn-primary btn-large"
                >
                  {{ isLoading ? 'Запуск собеседования...' : 'Начать собеседование' }}
                </button>
                <p class="hint">Собеседование состоит из {{ totalQuestions }} вопросов</p>
              </div>

              <div v-if="isFinished" class="result-section">
                <div :class="['result-card', interviewPassed ? 'success' : 'failure']">
                  <div class="result-icon">
                    {{ interviewPassed ? '✅' : '❌' }}
                  </div>
                  <div class="result-content">
                    <h3>{{ interviewPassed ? 'Собеседование пройдено!' : 'Собеседование не пройдено' }}</h3>
                    <p class="final-score">Финальный балл: <strong>{{ averageScore.toFixed(1) }}/5.0</strong></p>
                    <p class="result-message">
                      {{ interviewPassed 
                         ? 'Поздравляем! Вы успешно прошли техническое собеседование.' 
                         : 'К сожалению, ваш результат ниже проходного балла.' 
                      }}
                    </p>
                  </div>
                </div>
                <div class="result-actions">
                  <button @click="backToAnalysis" class="btn btn-outline">Вернуться к анализу</button>
                  <button @click="restartInterview" class="btn btn-primary">Пройти заново</button>
                </div>
              </div>
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
import { ref, computed, onMounted, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'

const router = useRouter()
const store = useAppStore()

// -------------------------------------------------------
// Reactive state
// -------------------------------------------------------
const sessionId = ref(null)
const messages = ref([])
const userAnswer = ref('')
const isLoading = ref(false)
const isFinished = ref(false)
const interviewPassed = ref(false)
const scores = ref([])
const currentQuestionNumber = ref(0)
const isListening = ref(false)
const isSpeechSupported = ref(false)

const messagesContainer = ref(null)
const speechRecognition = ref(null)

// -------------------------------------------------------
// Constants
// -------------------------------------------------------
const totalQuestions = 5
const passingScore = 3

// -------------------------------------------------------
// Computed
// -------------------------------------------------------
const currentTopic = computed(() => store.userData?.topic || 'software_developer')
const currentLanguage = computed(() => store.userData?.language || 'ru')

const averageScore = computed(() => {
  return scores.value.length
    ? scores.value.reduce((a, b) => a + b, 0) / scores.value.length
    : 0
})

// -------------------------------------------------------
// Helper: readable topic name
// -------------------------------------------------------
const getTopicName = (topic) => {
  const topics = {
    python: 'Python разработчик',
    java: 'Java разработчик',
    csharp: 'C# разработчик',
    javascript: 'JavaScript разработчик',
    cpp: 'C++ разработчик',
    other: 'Другое',
    software_developer: 'Разработчик ПО'
  }
  return topics[topic] || topic
}

// -------------------------------------------------------
// Chat helper
// -------------------------------------------------------
const addMessage = (text, type, score, reasoning) => {
  messages.value.push({ text, type, score, reasoning })
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// -------------------------------------------------------
// Speech recognition
// -------------------------------------------------------
const initializeSpeechRecognition = () => {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SR) return

  isSpeechSupported.value = true
  speechRecognition.value = new SR()
  speechRecognition.value.lang = currentLanguage.value === 'ru' ? 'ru-RU' : 'en-US'
  speechRecognition.value.interimResults = false

  speechRecognition.value.onresult = (e) => {
    userAnswer.value = e.results[0][0].transcript
    isListening.value = false
  }

  speechRecognition.value.onerror = () => {
    addMessage("Ошибка распознавания речи.", 'bot')
    isListening.value = false
  }
}

// -------------------------------------------------------
// Start interview
// -------------------------------------------------------
const startInterview = async () => {
  const interview = store.userData.interviewData

  if (!interview) {
    addMessage("Ошибка: данные интервью отсутствуют. Вернитесь назад.", 'bot')
    return
  }

  const resumeText = interview.resumeText || "";

  if (!resumeText.trim()) {
    addMessage("Ошибка: текст резюме отсутствует.", "bot")
    return
  }

  isLoading.value = true
  addMessage("Запуск собеседования...", "bot")

  try {
    const response = await fetch("http://localhost:8000/api/start_interview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_text: resumeText,
        language: currentLanguage.value,
        topic: currentTopic.value
      })
    })

    const data = await response.json()

    sessionId.value = data.session_id
    currentQuestionNumber.value = 1
    addMessage(data.question, "bot")

  } catch (err) {
    addMessage("Ошибка при запуске интервью", "bot")
  }

  isLoading.value = false
}

// -------------------------------------------------------
// Send answer
// -------------------------------------------------------
const sendAnswer = async () => {
  if (!userAnswer.value.trim()) return

  const answer = userAnswer.value.trim()
  addMessage(answer, "user")
  userAnswer.value = ''
  isLoading.value = true

  try {
    const response = await fetch("http://localhost:8000/api/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId.value,
        answer,
        language: currentLanguage.value
      })
    })

    const data = await response.json()

    if (data.score !== undefined) {
      const lastUser = messages.value[messages.value.length - 1]
      lastUser.score = data.score
      lastUser.reasoning = data.reasoning
      scores.value.push(data.score)
    }

    if (data.next_question) {
      currentQuestionNumber.value++
      addMessage(data.next_question, "bot")
    }

    if (data.finished) {
      isFinished.value = true
      interviewPassed.value = data.passed
      addMessage(
        data.passed
          ? "Собеседование завершено! Вы прошли!"
          : "Собеседование завершено. Вы не прошли.",
        "bot"
      )
    }

  } catch (err) {
    addMessage("Ошибка отправки ответа", "bot")
  }

  isLoading.value = false
}

// -------------------------------------------------------
const toggleVoiceInput = () => {
  if (!speechRecognition.value) return
  isListening.value = true
  speechRecognition.value.start()
}

// -------------------------------------------------------
const restartInterview = () => {
  sessionId.value = null
  messages.value = []
  scores.value = []
  isFinished.value = false
  interviewPassed.value = false
  currentQuestionNumber.value = 0
  addMessage("Нажмите 'Начать собеседование'", "bot")
}

// -------------------------------------------------------
// Lifecycle
// -------------------------------------------------------
onMounted(() => {
  store.loadFromStorage()

  if (!store.userData.interviewData) {
    router.push('/resume-analysis')
    return
  }

  initializeSpeechRecognition()

  addMessage(
    "Добро пожаловать на онлайн-собеседование! Нажмите 'Начать собеседование'.",
    "bot"
  )
})

onUnmounted(() => {
  speechRecognition.value?.stop()
})
</script>






























































<style scoped>
.interview-view {
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

.interview-section {
  width: 100%;
}

.interview-card {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.interview-header {
  text-align: center;
  margin-bottom: 30px;
}

.interview-header h2 {
  margin-bottom: 10px;
  color: #333;
  font-size: 2em;
}

.subtitle {
  color: #666;
  margin-bottom: 20px;
}

.interview-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  font-weight: 500;
  color: #555;
}

.value {
  color: #333;
  font-weight: 600;
}

.chat-container {
  height: 500px;
  display: flex;
  flex-direction: column;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.message {
  margin-bottom: 20px;
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message.bot {
  justify-content: flex-start;
}

.message-content {
  max-width: 70%;
  padding: 15px;
  border-radius: 12px;
  position: relative;
}

.message.user .message-content {
  background: #10b981;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.bot .message-content {
  background: white;
  border: 1px solid #e1e5e9;
  border-bottom-left-radius: 4px;
}

.message-sender {
  font-size: 0.8em;
  font-weight: 600;
  margin-bottom: 5px;
  opacity: 0.8;
}

.message-score {
  font-size: 0.8em;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.3);
}

.message.bot .message-score {
  border-top-color: #e1e5e9;
  color: #666;
}

.reasoning {
  font-style: italic;
  opacity: 0.8;
}

.typing {
  color: #666;
  font-style: italic;
}

.input-container {
  border-top: 1px solid #e1e5e9;
  padding-top: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.input-group textarea {
  width: 100%;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.input-group textarea:focus {
  border-color: #10b981;
  outline: none;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}

.input-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.start-section, .result-section {
  text-align: center;
  padding: 40px 20px;
}

.btn-large {
  padding: 15px 30px;
  font-size: 1.1em;
}

.result-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 30px;
  border-radius: 10px;
  margin-bottom: 20px;
  text-align: left;
}

.result-card.success {
  background: #f0fdf4;
  border: 2px solid #10b981;
}

.result-card.failure {
  background: #fef2f2;
  border: 2px solid #ef4444;
}

.result-icon {
  font-size: 3em;
}

.result-content h3 {
  margin-bottom: 10px;
  color: #333;
}

.final-score {
  font-size: 1.1em;
  margin-bottom: 10px;
}

.result-message {
  color: #666;
  margin-bottom: 0;
}

.result-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.hint {
  color: #666;
  font-size: 0.9em;
  margin-top: 10px;
}

.btn.listening {
  background: #ef4444;
  color: white;
  border-color: #ef4444;
}

/* Header & Footer styles (same as previous components) */
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

.btn-outline {
  background-color: transparent;
  color: #10b981;
  border: 1px solid #10b981;
}

.btn-outline:hover:not(:disabled) {
  background-color: #10b981;
  color: white;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.footer {
  background-color: #333;
  color: white;
  padding: 20px 0;
  text-align: center;
}

@media (max-width: 768px) {
  .interview-card {
    padding: 20px;
    margin: 20px;
  }
  
  .interview-info {
    grid-template-columns: 1fr;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .input-actions {
    flex-direction: column;
  }
  
  .result-actions {
    flex-direction: column;
  }
  
  .result-card {
    flex-direction: column;
    text-align: center;
  }
}
</style>