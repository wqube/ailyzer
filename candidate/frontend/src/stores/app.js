import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const userData = ref({
    fullName: '',
    email: '',
    phone: '',
    resumeText: '',
    resumeAnalysis: null,
    interviewData: null,
    topic: 'software_developer', // тема собеседования
    language: 'ru'  
  })

  // Сохранение данных резюме
  function setResumeData(data) {
    userData.value.fullName = data.fullName
    userData.value.email = data.email
    userData.value.phone = data.phone
    userData.value.resumeText = data.resumeText || data.parsed_text || ""    
    saveToStorage()
  }

  // Сохранение результата анализа
  function setResumeAnalysis(result) {
    userData.value.resumeAnalysis = result

  if (result.parsed_text) {
    userData.value.resumeText = result.parsed_text
  }
    saveToStorage()
  }

  // Подготовка данных для интервью
  function prepareInterviewData() {
    userData.value.interviewData = {
      fullName: userData.value.fullName,
      email: userData.value.email,
      phone: userData.value.phone,
      resumeText: userData.value.resumeText,
      resumeAnalysis: userData.value.resumeAnalysis
      
    }

    saveToStorage()
  }
function setLanguage(lang) {
    userData.value.language = lang
    saveToStorage()
    
  }
   function setTopic(topic) {
    userData.value.topic = topic
    saveToStorage()
  }
  // Сохранение в localStorage
  function saveToStorage() {
    localStorage.setItem('user_data', JSON.stringify(userData.value))
  }

  // Загрузка
  function loadFromStorage() {
    const stored = localStorage.getItem('user_data')
    if (stored) {
      userData.value = JSON.parse(stored)
    }
  }

  // Очистка
  function clearData() {
    userData.value = {
      fullName: '',
      email: '',
      phone: '',
      resumeText: '',
      resumeAnalysis: null,
      interviewData: null,
      topic: 'software_developer',
      language: 'ru'
    }
    localStorage.removeItem('user_data')
  }

  return {
    userData,
    setResumeData,
    setResumeAnalysis,
    setTopic,
    setLanguage,
    prepareInterviewData,
    saveToStorage,
    loadFromStorage,
    clearData
  }
})
