<template>
        <section class="auth-section">
            <div class="container">
                <div class="auth-card">
                    <h2>Вход в аккаунт</h2>
                    <form class="auth-form" @submit.prevent="handleLogin">
                        <div class="form-group">
                            <label for="login">Номер телефона или email *</label>
                            <input type="text" id="login" v-model="loginForm.login" required>
                        </div>
          
                        <div class="form-group">
                            <label for="password">Пароль *</label>
                            <input type="password" id="password" v-model="loginForm.password" required>
                        </div>
          
                        <div class="form-options">
                            <label class="checkbox">
                                <input type="checkbox" v-model="loginForm.remember">
                                <span class="checkmark"></span>
                                Запомнить меня
                            </label>
                            <a href="#" class="forgot-password">Забыли пароль?</a>
                        </div>
          
                        <div class="form-actions">
                            <button type="submit" class="btn btn-primary btn-full">Войти</button>
                        </div>
          
                        <div class="auth-links">
                            <p>Нет аккаунта? 
                            <a href="#" @click.prevent="$emit('navigate', 'registration')">Зарегистрироваться</a>
                            </p>
                        </div>
                    </form>
                </div>
            </div>
        </section>
</template>

<script>
    export default {
    name: 'Login',
    emits: ['navigate'],

    data() {
        return {
        loginForm: {
        login: '',
        password: '',
        remember: false
        }
        }
    },
    methods: {
        handleLogin() {
        // Здесь будет логика входа
        console.log('Login attempt:', this.loginForm)
        // После успешного входа перенаправить на другую страницу
        },
        navigateTo(page) {
            this.$emit('navigate', page);
        }
    }
    }
</script>