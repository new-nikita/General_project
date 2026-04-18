<template>
  <div class="reset-password">
    <h2>Новый пароль</h2>
    <form @submit.prevent="submitPassword">
      <label for="new_password">Новый пароль:</label>
      <input
        type="password"
        id="new_password"
        v-model="newPassword"
        required
      />

      <label for="confirm_password">Подтвердите пароль:</label>
      <input
        type="password"
        id="confirm_password"
        v-model="confirmPassword"
        required
      />

      <button type="submit">Сменить пароль</button>
    </form>

    <p v-if="message" :class="{ success: success, error: !success }">{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import { authApi } from "@/api/generated/auth/auth";

const route = useRoute();
const token = route.query.token as string;

const newPassword = ref("");
const confirmPassword = ref("");
const message = ref("");
const success = ref(false);

const submitPassword = async () => {
  try {
    const response = await authApi.resetPassword({
      token,
      new_password: newPassword.value,
      confirm_password: confirmPassword.value
    });
    message.value = response.message;
    success.value = response.success;
  } catch (err: any) {
    message.value = err.response?.data?.detail || "Ошибка при смене пароля";
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