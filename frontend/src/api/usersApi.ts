// frontend/src/api/usersApi.ts
import { api } from "@/api/client"

export const getUsers = async () => {
  const res = await api.get("/users/profile")
  return res
}

export const fetchProfile = async (userId: number) => {
  const res = await api.get(`/users/profile/${userId}`)
  return res
}
