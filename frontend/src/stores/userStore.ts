import { defineStore } from "pinia"
import axios from "axios"

export const useUserStore = defineStore("userStore", {
  state: () => ({
    user: null as null | Record<string, any>,
    posts: [] as any[],
  }),
  actions: {
    async fetchProfile(id: number) {
      const res = await axios.get(`/api/users/${id}`)
      this.user = res.data
    },
    async createPost(content: string) {
      const res = await axios.post("/api/posts", { content })
      this.posts.push(res.data)
    },
  },
})