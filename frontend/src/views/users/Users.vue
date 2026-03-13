<script setup lang="ts">
import { ref, onMounted } from "vue"
import { getUsers } from "@/api/users.api.ts"
import type { User } from "@/types/user.ts"

const users = ref<User[]>([])

onMounted(async () => {
  const response = await getUsers()
  users.value = response.data
})
</script>

<template>
  <div>
    <div v-for="user in users" :key="user.id">
      {{ user.name }}
    </div>
  </div>
</template>