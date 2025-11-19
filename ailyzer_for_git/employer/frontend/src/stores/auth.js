import { defineStore } from 'pinia';
import { authUtils } from '@/utils/api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: false,
    user: null
  }),

  actions: {
    // Проверяем статус аутентификации
    checkAuth() {
      this.isAuthenticated = authUtils.isAuthenticated();
      return this.isAuthenticated;
    },

    // Устанавливаем аутентификацию
    setAuthenticated(status) {
      this.isAuthenticated = status;
    },

    // Выход из системы
    async logout() {
      try {
        const tokens = authUtils.getTokens();
        if (tokens.refresh_token) {
          const { api } = await import('@/utils/api');
          await api.logoutUser(tokens.refresh_token);
        }
      } catch (error) {
        console.error('Logout error:', error);
      } finally {
        authUtils.clearTokens();
        this.isAuthenticated = false;
        this.user = null;
      }
    }
  }
});