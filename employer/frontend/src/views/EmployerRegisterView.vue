<template>
  <div class="employer-auth">
    <div class="auth-container">
      <div class="auth-card">
        <h1>Регистрация работодателя</h1>
        
        <form class="auth-form" @submit.prevent="handleRegister">
          <div class="form-group">
            <label for="email">Корпоративный email *</label>
            <input 
              type="email" 
              id="email" 
              v-model="registerData.email" 
              required 
              placeholder="your@company.com"
            >
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="lastName">Фамилия *</label>
              <input 
                type="text" 
                id="lastName" 
                v-model="registerData.lastName" 
                required
              >
            </div>

            <div class="form-group">
              <label for="firstName">Имя *</label>
              <input 
                type="text" 
                id="firstName" 
                v-model="registerData.firstName" 
                required
              >
            </div>
          </div>

          <div class="form-group">
            <label for="middleName">Отчество</label>
            <input 
              type="text" 
              id="middleName" 
              v-model="registerData.middleName"
            >
          </div>

          <div class="form-group">
            <label for="phone">Телефон *</label>
            <input 
              type="tel" 
              id="phone" 
              v-model="registerData.phone" 
              required
            >
          </div>

          <div class="form-group">
            <label for="position">Должность *</label>
            <input 
              type="text" 
              id="position" 
              v-model="registerData.position" 
              required
            >
          </div>

          <div class="form-group">
            <label for="company">Компания *</label>
            <input 
              type="text" 
              id="company" 
              v-model="registerData.company" 
              required
            >
          </div>

          <div class="form-group">
            <label for="city">Город *</label>
            <input 
              type="text" 
              id="city" 
              v-model="registerData.city" 
              required
            >
          </div>

          <div class="form-group">
            <label for="password">Пароль *</label>
            <input 
              type="password" 
              id="password" 
              v-model="registerData.password" 
              required 
              placeholder="Не менее 6 символов"
              minlength="6"
            >
          </div>

          <div class="form-group">
            <label for="confirmPassword">Подтверждение пароля *</label>
            <input 
              type="password" 
              id="confirmPassword" 
              v-model="registerData.confirmPassword" 
              required 
              placeholder="Повторите пароль"
            >
          </div>

          <div class="form-actions">
            <button 
              type="submit" 
              class="btn btn-primary btn-full"
              :disabled="loading"
            >
              {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
            </button>
          </div>

          <div class="auth-links">
            <p>Уже есть аккаунт? 
              <router-link to="/employer/login">Войти</router-link>
            </p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth';
import { api, authUtils } from '@/utils/api'

export default {
  name: 'EmployerRegisterView',

  setup() {
    const authStore = useAuthStore();
    return { authStore };
  },

  data() {
    return {
      registerData: {
        email: '',
        lastName: '',
        firstName: '',
        middleName: '',
        phone: '',
        position: '',
        company: '',
        city: '',
        password: '',
        confirmPassword: ''
      },
      loading: false
    }
  },
  methods: {
    async handleRegister() {
      // Валидация паролей
      if (this.registerData.password !== this.registerData.confirmPassword) {
        alert('Пароли не совпадают')
        return
      }

      if (this.registerData.password.length < 6) {
        alert('Пароль должен содержать не менее 6 символов')
        return
      }
      
      this.loading = true
      try {
        const result = await api.registerUser({
          email: this.registerData.email,
          password: this.registerData.password
        })

        // ИСПРАВЛЕНО: Сохраняем токены после успешной регистрации
        if (result.access_token && result.refresh_token) {
          authUtils.saveTokens(result);
          this.authStore.setAuthenticated(true);
          
          // Перенаправляем сразу в дашборд после успешной регистрации
          this.$router.push({ name: 'employer-dashboard' });
        } else {
          // Если токены не пришли, просим пользователя войти
          alert('Регистрация успешна! Теперь вы можете войти в систему.');
          this.$router.push({ name: 'employer-login' });
        }
        
      } catch (error) {
        alert(error.message)
      } finally {
        this.loading = false
      }
    }
  },

  mounted() {
    // ДОБАВЛЕНО: Если пользователь уже авторизован, перенаправляем в дашборд
    if (this.authStore.isAuthenticated) {
      this.$router.push({ name: 'employer-dashboard' });
    }
  }
}
</script>

<style scoped>
.employer-auth {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 0;
}

.auth-container {
  width: 100%;
  max-width: 500px;
}

.auth-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.auth-card h1 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.btn-full {
  width: 100%;
}

.auth-links {
  text-align: center;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.auth-links a {
  color: #007bff;
  text-decoration: none;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .auth-container {
    max-width: 100%;
    padding: 0 1rem;
  }
}
</style>