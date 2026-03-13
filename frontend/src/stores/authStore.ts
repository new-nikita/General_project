import { defineStore } from "pinia"

export const useAuthStore = defineStore("authStore", {
  state: () => ({
    user: null as null | { id: number; username: string },
  }),
  actions: {
    async login(data: { username: string; password: string }) {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      })
      if (!res.ok) throw new Error("Неверный логин или пароль")
      this.user = await res.json()
    },
    async register(data: FormData) {
      const res = await fetch("/api/auth/register", {
        method: "POST",
        body: data,
      })
      if (!res.ok) throw new Error("Ошибка регистрации")
    },
  },
})