import { createRouter, createWebHistory } from 'vue-router'

import MainPageView from '@/views/MainPageView.vue'
import EmployerLoginView from '@/views/EmployerLoginView.vue'
import EmployerRegisterView from '@/views/EmployerRegisterView.vue'
import EmployerDashboardView from '@/views/EmployerDashboardView.vue'
import VacanciesView from '@/views/VacanciesView.vue'

// Guard для защиты маршрутов, требующих аутентификации
const requireAuth = (to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    next()
  } else {
    next({ name: 'employer-login' })
  }
}

// Guard для редиректа, если пользователь уже авторизован
const redirectIfAuthenticated = (to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    next({ name: 'employer-dashboard' })
  } else {
    next()
  }
}

const routes = [
    // Главная страница
    {
        path: '/',
        name: 'mainpage',
        component: MainPageView,
        meta: { title: 'Главная страница' }
    },

  // Маршруты для работодателей
  {
    path: '/employer/login',
    name: 'employer-login',
    component: EmployerLoginView,
    meta: { title: 'Вход для работодателей' },
    beforeEnter: redirectIfAuthenticated
  },
  {
    path: '/employer/register',
    name: 'employer-register',
    component: EmployerRegisterView,
    meta: { title: 'Регистрация работодателя' },
    beforeEnter: redirectIfAuthenticated
  },
  {
    path: '/employer/dashboard',
    name: 'employer-dashboard',
    component: EmployerDashboardView,
    meta: { title: 'Дашборд работодателя', requiresAuth: true },
    beforeEnter: requireAuth
  },

  //Для вакансий
  {
  path: '/employer/vacancies',
  name: 'employer-vacancies',
  component: VacanciesView,
  meta: { title: 'Мои вакансии', requiresAuth: true },
  beforeEnter: requireAuth
  },

  //Для кандидатов на вакнсии
  {
  path: '/employer/vacancies/:vacancyId/candidates',
  name: 'employer-candidates',
  component: () => import('@/views/CandidatesView.vue'),
  meta: { title: 'Кандидаты', requiresAuth: true },
  beforeEnter: requireAuth
  },
  //////////////////////
  
  // Редирект с корня на логин работодателя
  {
    path: '/',
    redirect: '/employer/login'
  },
  
  // Редирект для неизвестных маршрутов
  {
    path: '/:pathMatch(.*)*',
    redirect: '/employer/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Глобальный navigation guard
router.beforeEach((to, from, next) => {
  // Устанавливаем заголовок страницы
  if (to.meta.title) {
    document.title = `${to.meta.title} | AIlyzer`
  }
  
  // Проверяем требуется ли аутентификация для маршрута
  if (to.matched.some(record => record.meta.requiresAuth)) {
    const token = localStorage.getItem('access_token')
    if (!token) {
      next({ name: 'employer-login' })
      return
    }
  }
  
  next()
})

export default router