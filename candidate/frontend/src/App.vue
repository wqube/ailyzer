<template>
  <div class="app">
    <Header @navigate="changePage"></Header>

    <main class="main-content">
      <router-view></router-view>
    </main>

    <Footer></Footer>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
// Предполагаем, что компоненты Header и Footer существуют и импортированы
// Если они находятся в других путях, скорректируйте импорт:
import Header from './components/Header.vue';
import Footer from './components/Footer.vue';

const router = useRouter();
const route = useRoute();

// --- Методы навигации (для использования в Header.vue) ---
const changePage = (page) => {
  // Карта маршрутов для навигации кандидата
  const routes = {
    // '/contact' - форма контактных данных, может быть также '/'
    'contact': '/', 
    'analysis': '/resume-analysis', 
    'interview': '/interview'
  };
  
  if (routes[page]) {
    router.push(routes[page]);
  } else if (page === 'home') {
    // Дополнительная логика для главной страницы или перехода на /
    router.push('/');
  }
};

// --- Дополнительная логика (аналогичная 'pageTitle' из примера) ---
const pageTitle = computed(() => {
  const routeName = route.name;
  const titles = {
    'data-form': 'Контактные данные',
    'resume-analysis': 'Анализ резюме',
    'interview': 'Собеседование с ИИ',
    // 'vacancy-form': 'Заполнение вакансии'
  };
  return titles[routeName] || 'Ailyzer';
});

// Если вам нужно отслеживать currentPage для передачи в дочерние компоненты,
// вы можете сделать это с помощью watch, но для Vue 3 это чаще всего не требуется, 
// так как дочерние компоненты могут напрямую использовать `useRoute()`.

</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

</style>