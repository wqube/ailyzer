import { createRouter, createWebHistory } from 'vue-router'
import DataFormView from '@/views/DataFormView.vue'
import ResumeAnalysisView from '@/views/ResumeAnalysisView.vue'
import InterviewView from '@/views/InterviewView.vue'

const routes = [
  {
    path: '/',
    name: 'data-form',
    component: DataFormView
  },
  {
    path: '/:id', // Ссылка с ID вакансии
    name: 'data-form-vacancy',
    component: DataFormView,
    props: true
  },
  {
    path: '/resume-analysis',
    name: 'resume-analysis',
    component: ResumeAnalysisView
  },
  {
    path: '/resume-analysis/:id', // Анализ резюме для конкретной вакансии
    name: 'resume-analysis-vacancy', 
    component: ResumeAnalysisView,
    props: true
  },
  {
    path: '/interview',
    name: 'interview',
    component: InterviewView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router