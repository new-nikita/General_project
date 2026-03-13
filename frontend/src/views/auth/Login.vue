<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"

const auth = useAuthStore()
const router = useRouter()

const username = ref("")
const password = ref("")
const remember = ref(false)

const error = ref("")
const loading = ref(false)

async function submitLogin() {

  error.value = ""
  loading.value = true

  try {

    await auth.login(username.value, password.value)

    router.push(`/profile/${auth.currentUser.id}`)

  } catch (e) {

    error.value = "Неверный логин или пароль"

  } finally {

    loading.value = false

  }

}
</script>

<template>

<div class="container">

  <div class="row justify-content-center">

    <div class="col-md-8 col-lg-6">

      <div class="login-container">

        <h1 class="login-title">
          Вход в систему
        </h1>

        <!-- ERROR -->

        <div
          v-if="error"
          class="login-error"
        >
          <i class="fas fa-exclamation-circle me-2"></i>
          {{ error }}
        </div>

        <form @submit.prevent="submitLogin">

          <!-- USERNAME -->

          <div class="mb-4">

            <div class="input-group">

              <span class="input-group-text bg-transparent">

                <i class="fas fa-user text-muted"></i>

              </span>

              <input
                v-model="username"
                type="text"
                class="form-control input-with-icon"
                placeholder="Имя пользователя"
                required
              >

            </div>

          </div>


          <!-- PASSWORD -->

          <div class="mb-4">

            <div class="input-group">

              <span class="input-group-text bg-transparent">

                <i class="fas fa-lock text-muted"></i>

              </span>

              <input
                v-model="password"
                type="password"
                class="form-control input-with-icon"
                placeholder="Пароль"
                required
              >

            </div>

          </div>


          <!-- LOGIN BUTTON -->

          <button
            class="btn btn-login btn-primary w-100 mb-3"
            :disabled="loading"
          >

            <i class="fas fa-sign-in-alt me-2"></i>

            {{ loading ? "Входим..." : "Войти" }}

          </button>


          <!-- REMEMBER -->

          <div class="d-flex justify-content-between align-items-center">

            <div class="form-check">

              <input
                v-model="remember"
                class="form-check-input"
                type="checkbox"
                id="rememberMe"
              >

              <label
                class="form-check-label"
                for="rememberMe"
              >
                Запомнить меня
              </label>

            </div>

            <RouterLink to="/forgot_password">
              Забыли пароль?
            </RouterLink>

          </div>

        </form>


        <!-- FOOTER -->

        <div class="login-footer mt-4">

          Ещё нет аккаунта?

          <RouterLink to="/initial_register">
            Зарегистрироваться
          </RouterLink>

        </div>

      </div>

    </div>

  </div>

</div>

</template>