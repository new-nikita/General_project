<template>
  <form @submit.prevent="submit">
    <input v-model="form.username" placeholder="Username" />
    <input v-model="form.email" placeholder="Email" type="email" />
    <input v-model="form.password" placeholder="Password" type="password" />
    <input v-model="form.password2" placeholder="Repeat Password" type="password" />
    <input type="file" @change="onFileChange" />

    <button type="submit" :disabled="loading">Register</button>
  </form>

  <p v-if="error" style="color:red">{{ error }}</p>
  <p v-if="success" style="color:green">{{ success }}</p>
</template>

<script lang="ts">
import { ref } from "vue";
import { useRegister } from "../composables/useRegister";

export default {
  setup() {
    const { loading, error, success, registerUser } = useRegister();

    const form = ref({
      username: "",
      email: "",
      password: "",
      password2: "",
      first_name: "",
      last_name: "",
    });

    const avatarFile = ref<File | null>(null);

    function onFileChange(e: Event) {
      const target = e.target as HTMLInputElement;
      if (target.files && target.files.length > 0) {
        avatarFile.value = target.files[0];
      }
    }

    async function submit() {
      await registerUser(form.value, avatarFile.value ?? undefined);
    }

    return { form, loading, error, success, submit, onFileChange };
  },
};
</script>