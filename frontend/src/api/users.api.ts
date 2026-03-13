// src/api/users.api.ts
import axios from "axios"

export const getUsers = async () => {
  const res = await axios.get("/api/users")
  return res.data
}