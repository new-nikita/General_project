<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/authStore"

const router = useRouter()
const auth = useAuthStore()

const username = ref("")
const password = ref("")
const remember = ref(false)

const error = ref("")
const loading = ref(false)

async function login() {

  error.value = ""
  loading.value = true

  try {

    await auth.login({
      username: username.value,
      password: password.value,
      remember: remember.value
    })

    router.push("/")

  } catch (e:any) {

    error.value = e?.message || "Ошибка входа"

  } finally {

    loading.value = false

  }

}
</script>

<template>

<div class="login-page">

<div class="login-container">

<h1 class="login-title">
Вход в систему
</h1>

<div v-if="error" class="login-error">
{{ error }}
</div>

<form @submit.prevent="login">

<div class="input-group">

<span class="icon">
👤
</span>

<input
v-model="username"
type="text"
placeholder="Имя пользователя"
required
/>

</div>

<div class="input-group">

<span class="icon">
🔒
</span>

<input
v-model="password"
type="password"
placeholder="Пароль"
required
/>

</div>

<button
class="btn-login"
:disabled="loading"
>

{{ loading ? "Вход..." : "Войти" }}

</button>

<div class="login-options">

<label>

<input
type="checkbox"
v-model="remember"
/>

Запомнить меня

</label>

<router-link to="/forgot-password">
Забыли пароль?
</router-link>

</div>

</form>

<div class="login-footer">

Ещё нет аккаунта?

<router-link to="/register">
Зарегистрироваться
</router-link>

</div>

</div>

</div>

</template>

<style scoped>

.login-page{

display:flex;
justify-content:center;
align-items:center;

min-height:80vh;

}

.login-container{

width:100%;
max-width:420px;

padding:40px;

background:white;

border-radius:12px;

box-shadow:0 10px 30px rgba(0,0,0,0.1);

}

.login-title{

text-align:center;
margin-bottom:30px;

}

.login-error{

background:#ffeded;
color:#d00000;

padding:10px;
margin-bottom:20px;

border-radius:6px;

}

.input-group{

display:flex;
align-items:center;

border:1px solid #ddd;

border-radius:8px;

margin-bottom:16px;

overflow:hidden;

}

.icon{

padding:10px;
background:#f5f5f5;

}

input{

flex:1;

border:none;
padding:12px;

outline:none;

}

.btn-login{

width:100%;

padding:12px;

border:none;

background:#4a76a8;
color:white;

border-radius:8px;

font-size:16px;

cursor:pointer;

margin-top:10px;

}

.login-options{

display:flex;
justify-content:space-between;

margin-top:15px;

font-size:14px;

}

.login-footer{

margin-top:25px;

text-align:center;

}

</style>