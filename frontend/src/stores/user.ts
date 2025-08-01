import http from '@/http'
import { defineStore } from 'pinia'
import {
  USER_USERNAME_KEY,
  USER_IS_STAFF_KEY,
} from '@/constants'


export const useUserStore = defineStore('user', {
  state: () => ({
    username: localStorage.getItem(USER_USERNAME_KEY) as string || '',
    isStaff: localStorage.getItem(USER_IS_STAFF_KEY) === 'true'
  }),
  actions: {
    async loadMe () {
      const res = await http.get('/api/user/me/')
      this.username = res.data.username
      this.isStaff = res.data.is_staff
      localStorage.setItem(USER_USERNAME_KEY, res.data.username)
      localStorage.setItem(USER_IS_STAFF_KEY, res.data.is_staff.toString())
    }
  }
})
