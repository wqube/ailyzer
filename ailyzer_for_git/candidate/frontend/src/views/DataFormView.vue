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
          <div class="form-card">
            <h2>Заполните ваш профиль</h2>
            <p class="subtitle">Эта информация поможет нам подобрать для вас подходящие вакансии</p>
            
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
                <button type="submit" class="btn btn-primary btn-full">Отправить</button>
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
import { useRouter } from 'vue-router'

const router = useRouter()
const appStore = useAppStore()

const formData = ref({
  fullName: '',
  email: '',
  phone: '',
})

onMounted(() => {
  appStore.loadFromStorage()
  if (appStore.userData) {
    formData.value.fullName = appStore.userData.fullName || ''
    formData.value.email = appStore.userData.email || ''
    formData.value.phone = appStore.userData.phone || ''
  }
})

const submitForm = () => {
  appStore.setResumeData({
    fullName: formData.value.fullName,
    email: formData.value.email,
    phone: formData.value.phone,
    resumeText: appStore.userData.resumeText ?? ''
  })

  router.push('/resume-analysis')
}
</script>

<style scoped>
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

.form-card {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
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
  
  .profile-form .form-row {
    flex-direction: column;
    gap: 0;
  }
  
  .form-card {
    padding: 30px 20px;
    margin: 20px;
  }
  
  .form-card h2 {
    font-size: 1.5em;
  }
}
</style>