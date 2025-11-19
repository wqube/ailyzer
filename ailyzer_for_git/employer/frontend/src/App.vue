<script>
import Footer from './components/Footer.vue';
import Header from './components/Header.vue';

export default {
    name: 'App',
    components: {
        Header,
        Footer
    },
    data() {
        return {
            currentPage: 'mainpage'
        }
    },
    computed: {
        // Определяем текущую страницу на основе маршрута
        pageTitle() {
            const routeName = this.$route.name;
            const titles = {
                'employer-login': 'Вход для работодателя',
                'employer-register': 'Регистрация работодателя',
                'employer-dashboard': 'Дашборд работодателя',
                'mainpage': 'Главная страница'
            };
            return titles[routeName] || 'AIlyzer';
        }
    },
    methods: {
        changePage(page) {
            // Навигация через Vue Router
            const routes = {
                // 'mainpage': '/employer/dashboard',
                'mainpage': '/',
                'login': '/employer/login',
                'registration': '/employer/register'
            };
            
            if (routes[page]) {
                this.$router.push(routes[page]);
            }
        },
        
        // Метод для определения активной страницы в Header
        getCurrentPage() {
            const routeName = this.$route.name;
            const pageMap = {
                'employer-login': 'login',
                'employer-register': 'registration',
                'employer-dashboard': 'dashboard'
            };
            return pageMap[routeName] || 'mainpage';
        }
    },
    mounted() {
        // Инициализация текущей страницы при загрузке
        this.currentPage = this.getCurrentPage();
    },
    watch: {
        // Отслеживаем изменения маршрута
        '$route'(to) {
            this.currentPage = this.getCurrentPage();
        }
    }
}
</script>

<template>
    <div class="app">
        <Header :currentPage="currentPage" @navigate="changePage"></Header>

        <main class="main-content">
            <router-view></router-view>
        </main>

        <Footer></Footer>
    </div>
</template>

<style scoped>
.app {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.main-content {
    flex: 1;
    padding: 0;
}
</style>