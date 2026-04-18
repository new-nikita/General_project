<template>
  <div class="forgot-password">
    <h2>Сброс пароля</h2>
    <form @submit.prevent="submitEmail">
      <label for="email">Email:</label>
      <input
        type="email"
        id="email"
        v-model="email"
        required
      />
      <button type="submit">Отправить ссылку</button>
    </form>
    <p v-if="message" :class="{ success: success, error: !success }">{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { authApi } from "@/api/generated/auth/auth";

const email = ref("");
const message = ref("");
const success = ref(false);

const submitEmail = async () => {
  try {
    const response = await authApi.requestReset({ email: email.value });
    message.value = response.message;
    success.value = response.success;
  } catch (err: any) {
    message.value = err.response?.data?.detail || "Ошибка при отправке email";
    success.value = false;
  }
};
</script>

<style scoped>
.success {
  color: green;
}
.error {
  color: red;
}
</style>