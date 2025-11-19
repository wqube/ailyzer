<template>
    <header class="header">
        <div class="container">
            <div class="logo">
                <h1 @click="navigateTo('mainpage')">Ailyzer</h1>
            </div>

            <div class="header-actions">
                <span class="page-title">{{ pageTitle }}</span>
                <div class="auth-buttons">
                    <!-- Кнопки для НЕавторизованных пользователей -->
                    <template v-if="!authStore.isAuthenticated">
                        <button 
                            v-if="currentPage !== 'registration'" 
                            @click="navigateTo('registration')" 
                            class="btn btn-outline"
                        >
                            Регистрация
                        </button>
              
                        <button 
                            v-if="currentPage !== 'login'" 
                            @click="navigateTo('login')" 
                            class="btn btn-outline"
                        >
                            Вход
                        </button>
                    </template>

                    <!-- Кнопка для авторизованных пользователей -->
                    <template v-if="authStore.isAuthenticated">

                        <button  
                        @click="handleLogout" 
                        class="btn btn-primary"
                    >
                        Выйти
                    </button>

                    <button 
                        v-if="currentPage !== 'dashboard'" 
                        @click="navigateTo('dashboard')" 
                        class="btn btn-primary"
                    >
                        Дашборд
                    </button>

                    </template>
                </div>
            </div>
        </div>
    </header>
</template>

<script>
import { useAuthStore } from '@/stores/auth';
import { authUtils } from '@/utils/api';

export default {
    name: 'Header',
    props: {
        currentPage: String
    },
    emits: ['navigate'],
    
    setup() {
        const authStore = useAuthStore();
        
        // Проверяем аутентификацию при инициализации
        authStore.checkAuth();
        
        return {
            authStore
        };
    },

    computed: {
        pageTitle() {
            const titles = {
                mainpage: 'Главная страница',
                login: 'Вход для работодателя',
                registration: 'Регистрация работодателя',
                dashboard: 'Дашборд работодателя'
            };
            return titles[this.currentPage] || 'AIlyzer';
        }
    },

    methods: {
        navigateTo(page) {
            this.$emit('navigate', page);
        },

        async handleLogout() {
            await this.authStore.logout();
            
            // Переходим на главную если мы на dashboard
            if (this.currentPage === 'dashboard') {
                this.navigateTo('mainpage');
            }
        }
    },

    watch: {
        // Отслеживаем изменения страницы и проверяем аутентификацию
        currentPage() {
            this.authStore.checkAuth();
        }
    }
}
</script>