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
    path: '/resume-analysis',
    name: 'resume-analysis',
    component: ResumeAnalysisView
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
