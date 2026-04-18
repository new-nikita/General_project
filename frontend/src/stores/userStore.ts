import { defineStore } from "pinia"
import axios from "axios"

export const useUserStore = defineStore("user", {

  state: () => ({
    profile: null,
    posts: []
  }),

  actions: {

    async fetchProfile(userId) {
      try {

        const res = await axios.get(`/users/${userId}`)

        // 🔥 ВАЖНО: сохраняем в стор
        this.profile = res.data.user
        this.posts = res.data.posts || []

        // 🔥 ВАЖНО: возвращаем данные
        return {
          user: res.data.user,
          posts: res.data.posts || [],
          is_own_profile: res.data.is_own_profile
        }

      } catch (e) {
        console.error("FETCH PROFILE ERROR:", e)

        return {
          user: null,
          posts: [],
          is_own_profile: false
        }
      }
    }

  }

})