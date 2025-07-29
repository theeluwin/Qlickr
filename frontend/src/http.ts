import axios from 'axios'

import { useAuthStore } from '@/stores/auth'


let onHttpUnauthorized: (() => void) | null = null

const http = axios.create({
  withCredentials: true
})


http.interceptors.response.use(
  (res) => {
    return res
  },
  async (err) => {
    const authStore = useAuthStore()
    const originalRequest = err.config
    if (originalRequest && err.response?.status === 401) {
      if (originalRequest.url.endsWith('/api/token/refresh/')) {
        throw err
      }
      try {
        await authStore.refreshToken()
        return http(originalRequest)
      } catch (refreshError) {
        if (onHttpUnauthorized) {
          onHttpUnauthorized()
        }
      }
    }
    throw err
  }
)

export const setHttpUnauthorizedHandler = (handler: () => void) => {
  onHttpUnauthorized = handler
}

export default http
