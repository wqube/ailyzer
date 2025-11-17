<script>
    import Footer from './components/Footer.vue';
    import Header from './components/Header.vue';
    import MainPage from './components/MainPage.vue';
    import Registration from './components/Registration.vue';
    import Login from './components/Login.vue';

    export default {
        name: 'App',
        components: {
        Header,
        Footer,
        MainPage,
        Login,
        Registration
    },
    data() {
        return {
        currentPage: 'mainpage'
        }
    },
    methods: {
        changePage(page) {
        this.currentPage = page
        }
    }
    }
</script>

<template>
    
    <Header :currentPage="currentPage" @navigate="changePage"></Header>

    <main class="main-content">
        <MainPage v-if="currentPage === 'mainpage'" @navigate="changePage">  <</MainPage>
        <Login v-else-if="currentPage === 'login'" @navigate="changePage"> </Login>
        <Registration v-else-if="currentPage === 'registration'" @navigate="changePage"> </Registration>
    </main>

    <Footer></Footer>

</template>

<style scoped>

</style>
