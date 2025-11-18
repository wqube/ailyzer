<!-- <template>
    <header class="header">
        <div class="container">
            <div class="logo">
            <h1>Ailyzer</h1>
            </div>

            <div class="header-actions">
                <span class="page-title">{{ pageTitles[currentPage] }}</span>
                <div class="auth-buttons">
                    <button v-if="currentPage !== 'registration'" @click="$emit('navigate', 'registration')" class="btn btn-outline"> Регистрация </button>
          
                    <button v-if="currentPage !== 'login'" @click="$emit('navigate', 'login')" class="btn btn-outline"> Вход </button>
          
                    <button v-if="currentPage !== 'mainpage'" @click="$emit('navigate', 'mainpage')" class="btn btn-primary"> Главная </button>
                </div>
            </div>
        </div>
    </header>
</template>

<script>
    export default {
    name: 'Header',
    props: {
        currentPage: String
    },
    emits: ['navigate'],
    data() {
        return {
        pageTitles: {
            mainpage: 'Главная страница',
            login: 'Вход для работодателя',
            registration: 'Регистрация работодателя'
        }
        }
    },
    methods: {
        navigateTo(page) {
            this.$emit('navigate', page);
        }
    }
    }
</script> -->


<template>
    <header class="header">
        <div class="container">
            <div class="logo">
                <h1>Ailyzer</h1>
            </div>

            <div class="header-actions">
                <span class="page-title">{{ pageTitle }}</span>
                <div class="auth-buttons">
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
          
                    <button 
                        v-if="currentPage !== 'mainpage'" 
                        @click="navigateTo('mainpage')" 
                        class="btn btn-primary"
                    >
                        Главная
                    </button>

                    <button 
                        v-if="currentPage === 'dashboard'" 
                        @click="navigateTo('mainpage')" 
                        class="btn btn-primary"
                    >
                        Выйти
                    </button>
                </div>
            </div>
        </div>
    </header>
</template>

<script>
export default {
    name: 'Header',
    props: {
        currentPage: String
    },
    emits: ['navigate'],
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
        }
    }
}
</script>