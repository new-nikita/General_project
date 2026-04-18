import { defineStore } from "pinia"
import api from "@/api/client"

export const useAuthStore = defineStore("authStore", {
  state: () => ({
    user: null as null | { id: number; username: string },
  }),
  getters: {
    currentUser(): { id: number; username: string } | null {
      return this.user
    },
  },
  actions: {
    async login( { username: string; password: string }) {
      const form = new URLSearchParams()
      form.append("username", data.username)
      form.append("password", data.password)

      const res = await api.post("/api/v1/auth/login", form, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      })

      this.user = {
        id: res.data.user_id,
        username: res.data.username,
      }
    },

    async register( FormData) {
      await api.post("/api/v1/users/register", data)
    },

    async logout() {
      await api.get("/api/v1/auth/logout")
      this.user = null
    },
  },
})
