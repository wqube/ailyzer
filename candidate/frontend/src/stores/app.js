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
    topic: 'software_developer', // Удаляется, т.к. topic теперь в interviewData
    language: 'ru',
    // Поля для вакансии
    vacancyId: null,
    vacancyData: null
  })

  // Универсальный метод для обновления любых полей userData
  function setUserData(data) {
    // Используем Object.assign или spread для объединения данных
    Object.assign(userData.value, data)
    saveToStorage()
  }

  // Сохранение данных резюме (контакты + текст)
  function setResumeData(data) {
    userData.value.fullName = data.fullName
    userData.value.email = data.email
    userData.value.phone = data.phone
    // Используем resumeText из data, если он передан, иначе сохраняем текущий
    userData.value.resumeText = data.resumeText || userData.value.resumeText || ""
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
  function prepareInterviewData(payload = {}) {
    // В payload ожидаем {topic: string, resumeText: string}
    userData.value.interviewData = {
      fullName: userData.value.fullName,
      email: userData.value.email,
      phone: userData.value.phone,
      resumeText: payload.resumeText || userData.value.resumeText,
      topic: payload.topic || 'Общее техническое собеседование',
      language: userData.value.language,
      vacancyId: userData.value.vacancyId,
      vacancyData: userData.value.vacancyData
    }

    saveToStorage()
  }

  function setLanguage(lang) {
    userData.value.language = lang
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
      const parsed = JSON.parse(stored)
      // При объединении, чтобы избежать потери новых полей (как vacancyData), 
      // объединяем сохраненные данные с дефолтным состоянием
      Object.assign(userData.value, parsed)
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
      topic: '',
      language: 'ru',
      vacancyId: null,
      vacancyData: null
    }
    localStorage.removeItem('user_data')
  }

  return {
    userData,
    setUserData, // <-- НОВЫЙ/ОБНОВЛЕННЫЙ МЕТОД
    setResumeData,
    setResumeAnalysis,
    setLanguage,
    prepareInterviewData,
    saveToStorage,
    loadFromStorage,
    clearData
  }
})