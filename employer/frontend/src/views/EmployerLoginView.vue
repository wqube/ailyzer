<template>
  <div class="employer-auth">
    <div class="auth-container">
      <div class="auth-card">
        <h1>Вход для работодателей</h1>
        
        <form class="auth-form" @submit.prevent="handleLogin">
          <div class="form-group">
            <label for="email">Email *</label>
            <input 
              type="email" 
              id="email" 
              v-model="loginData.email" 
              required 
              placeholder="your@company.com"
            >
          </div>

          <div class="form-group">
            <label for="password">Пароль *</label>
            <input 
              type="password" 
              id="password" 
              v-model="loginData.password" 
              required 
              placeholder="Введите пароль"
            >
          </div>

          <div class="form-options">
            <label class="checkbox">
              <input type="checkbox" v-model="loginData.remember">
              <span class="checkmark"></span>
              Запомнить меня
            </label>
            <a href="#" class="forgot-password">Забыли пароль?</a>
          </div>

          <div class="form-actions">
            <button 
              type="submit" 
              class="btn btn-primary btn-full"
              :disabled="loading"
            >
              {{ loading ? 'Вход...' : 'Войти' }}
            </button>
          </div>

          <div class="auth-links">
            <p>Нет аккаунта? 
              <router-link to="/employer/register">Зарегистрироваться</router-link>
            </p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { api, authUtils } from '@/utils/api'

export default {
  name: 'EmployerLoginView',
  data() {
    return {
      loginData: {
        email: '',
        password: '',
        remember: false
      },
      loading: false
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      try {
        const result = await api.loginUser({
          email: this.loginData.email,
          password: this.loginData.password
        })
        
        authUtils.saveTokens(result)
        
        // Перенаправляем в дашборд
        this.$router.push({ name: 'employer-dashboard' })
        
      } catch (error) {
        alert(error.message)
      } finally {
        this.loading = false
      }
    }
  },
  mounted() {
    // Если пользователь уже авторизован, перенаправляем в дашборд
    if (authUtils.isAuthenticated()) {
      this.$router.push({ name: 'employer-dashboard' })
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
  max-width: 400px;
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

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox input {
  margin-right: 0.5rem;
}

.forgot-password {
  color: #007bff;
  text-decoration: none;
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
</style>