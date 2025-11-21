<template>
        <section class="auth-section">
            <div class="container">
                <div class="auth-card">
                    <h2>Создать аккаунт работодателя</h2>
                    <form class="auth-form" @submit.prevent="handleRegistration">
                        <div class="form-row">
                            <div class="form-group">
                            <label for="email">Корпоративный email *</label>
                            <input type="email" id="email" v-model="registrationForm.email" required>
                            </div>
                        </div>
          
                        <div class="form-row">
                            <div class="form-group">
                            <label for="lastName">Фамилия *</label>
                            <input type="text" id="lastName" v-model="registrationForm.lastName" required>
                            </div>

                            <div class="form-group">
                            <label for="firstName">Имя *</label>
                            <input type="text" id="firstName" v-model="registrationForm.firstName" required>
                            </div>
                        </div>
          
                        <div class="form-row">
                            <div class="form-group">
                            <label for="middleName">Отчество</label>
                            <input type="text" id="middleName" v-model="registrationForm.middleName">
                            </div>

                            <div class="form-group">
                            <label for="phone">Телефон *</label>
                            <input type="tel" id="phone" v-model="registrationForm.phone" required>
                            </div>
                        </div>
          
                        <div class="form-row">
                            <div class="form-group">
                            <label for="position">Должность *</label>
                            <input type="text" id="position" v-model="registrationForm.position" required>
                            </div>

                            <div class="form-group">
                            <label for="company">Компания *</label>
                            <input type="text" id="company" v-model="registrationForm.company" required></div>
                            </div>
          
                        <div class="form-row">
                            <div class="form-group">
                            <label for="city">Город *</label>
                            <input type="text" id="city" v-model="registrationForm.city" required>
                            </div>

                            <div class="form-group">
                            <label for="password">Пароль *</label>
                            <input type="password" id="password" v-model="registrationForm.password" required>
                            </div>
                        </div>
          
                        <div class="form-actions">
                            <button type="submit" class="btn btn-primary btn-full">Зарегистрироваться</button>
                        </div>
          
                        <div class="auth-links">
                            <p>Уже есть аккаунт? 
                            <a href="#" @click.prevent="$emit('navigate', 'login')">Войти</a>
                            </p>
                        </div>
                    </form>
                </div>
            </div>
        </section>
</template>

<script>
    export default {
    name: 'Registration',
    emits: ['navigate'],
        
    data() {
        return {
        registrationForm: {
        email: '',
        lastName: '',
        firstName: '',
        middleName: '',
        phone: '',
        position: '',
        company: '',
        city: '',
        password: ''
            }
        }
    },

    methods: {
        handleRegistration() {
        // Здесь будет логика регистрации
        console.log('Registration attempt:', this.registrationForm)
        // После успешной регистрации перенаправить на другую страницу
        },
        navigateTo(page) {
            this.$emit('navigate', page);
        }
    }
    }
</script>