import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const userData = ref({
    fullName: '',
    email: '',
    phone: '',
    // НОВЫЕ ПОЛЯ
    experience: null, // Опыт работы (лет)
    salaryExpectation: null, // Желаемая зарплата (RUB)
    
    resumeText: '',
    resumeAnalysis: null,
    interviewData: null,
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

  // Сохранение данных резюме (контакты + текст + НОВЫЕ ПОЛЯ)
  function setResumeData(data) {
    userData.value.fullName = data.fullName
    userData.value.email = data.email
    userData.value.phone = data.phone
    
    // !!! ИСПРАВЛЕНИЕ: Добавлены новые поля !!!
    userData.value.experience = data.experience || null
    userData.value.salaryExpectation = data.salaryExpectation || null
    
    // Используем resumeText из data, если он передан, иначе сохраняем текущий
    userData.value.resumeText = data.resumeText || userData.value.resumeText || ""
    saveToStorage()
  }

  // Сохранение результата анализа
  function setResumeAnalysis(result) {
    userData.value.resumeAnalysis = result

    if (result.parsed_text) {
      userData.value.resumeText = result.parsed_text
      // Опционально: можно обновить experience/salary из парсинга
      // if (result.metadata) {
      //     userData.value.experience = result.metadata.experience || userData.value.experience
      //     userData.value.salaryExpectation = result.metadata.salary_expectation || userData.value.salaryExpectation
      // }
    }
    saveToStorage()
  }

  // Подготовка данных для интервью
  function prepareInterviewData(payload = {}) {
    // В payload ожидаем {topic: string, resumeText: string, application_id: number}
    userData.value.interviewData = {
      fullName: userData.value.fullName,
      email: userData.value.email,
      phone: userData.value.phone,
      experience: userData.value.experience, // Передаем в интервью
      salaryExpectation: userData.value.salaryExpectation, // Передаем в интервью
      
      resumeText: payload.resumeText || userData.value.resumeText,
      topic: payload.topic || 'Общее техническое собеседование',
      language: userData.value.language,
      vacancyId: userData.value.vacancyId,
      vacancyData: userData.value.vacancyData,
      application_id: payload.application_id || null 
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
      // При объединении, чтобы избежать потери новых полей (как experience, salaryExpectation, vacancyData), 
      // объединяем сохраненные данные с дефолтным состоянием
      // Используем Object.assign для гарантированного обновления всех полей
      Object.assign(userData.value, parsed)
    }
  }

  // Очистка
  function clearData() {
    userData.value = {
      fullName: '',
      email: '',
      phone: '',
      experience: null, // Очищаем
      salaryExpectation: null, // Очищаем
      resumeText: '',
      resumeAnalysis: null,
      interviewData: null,
      language: 'ru',
      vacancyId: null,
      vacancyData: null
    }
    localStorage.removeItem('user_data')
  }

  return {
    userData,
    setUserData, 
    setResumeData,
    setResumeAnalysis,
    setLanguage,
    prepareInterviewData,
    saveToStorage,
    loadFromStorage,
    clearData
  }
})

// i'm still loving you