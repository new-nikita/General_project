<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/authStore"

const router = useRouter()
const auth = useAuthStore()

const loading = ref(false)
const error = ref("")

const form = ref({
  username: "",
  email: "",
  password: "",
  password2: "",

  first_name: "",
  last_name: "",
  middle_name: "",

  birth_date: "",
  gender: "",

  phone_number: "",

  country: "",
  city: "",
  street: "",

  bio: ""
})

const avatar = ref<File | null>(null)
const preview = ref<string | null>(null)

function onAvatarChange(e: Event) {

  const file = (e.target as HTMLInputElement).files?.[0]

  if (!file) return

  avatar.value = file
  preview.value = URL.createObjectURL(file)

}

async function register() {

  error.value = ""
  loading.value = true

  try {

    const data = new FormData()

    Object.entries(form.value).forEach(([k,v])=>{
      data.append(k,String(v))
    })

    if (avatar.value) {
      data.append("avatar", avatar.value)
    }

    await auth.register(data)

    router.push("/login")

  } catch (e:any) {

    error.value = e?.message || "Ошибка регистрации"

  } finally {

    loading.value = false

  }

}
</script>

<template>

<div class="register-page">

<div class="register-card">

<h2 class="title">
Создайте новый аккаунт
</h2>

<div v-if="error" class="error">
{{ error }}
</div>

<form @submit.prevent="register">

<h3>Основная информация</h3>

<input v-model="form.username" placeholder="Имя пользователя" required>

<input v-model="form.email" placeholder="Email" type="email" required>

<input v-model="form.password" type="password" placeholder="Пароль" required>

<input v-model="form.password2" type="password" placeholder="Повторите пароль" required>


<h3>Личная информация</h3>

<input v-model="form.first_name" placeholder="Имя">

<input v-model="form.last_name" placeholder="Фамилия">

<input v-model="form.middle_name" placeholder="Отчество">

<input v-model="form.birth_date" type="date">

<select v-model="form.gender">
<option value="">Пол</option>
<option value="male">Мужской</option>
<option value="female">Женский</option>
<option value="other">Другое</option>
</select>

<input v-model="form.phone_number" placeholder="Телефон">


<h3>Адрес</h3>

<input v-model="form.country" placeholder="Страна">

<input v-model="form.city" placeholder="Город">

<input v-model="form.street" placeholder="Улица">


<h3>О себе</h3>

<textarea
v-model="form.bio"
rows="3"
placeholder="Расскажите о себе"
/>


<h3>Аватар</h3>

<div class="avatar-upload">

<div class="avatar-preview">

<img
v-if="preview"
:src="preview"
/>

<div v-else class="avatar-placeholder">
👤
</div>

</div>

<input
type="file"
accept="image/*"
@change="onAvatarChange"
/>

</div>

<button
class="btn-register"
:disabled="loading"
>

{{ loading ? "Регистрация..." : "Зарегистрироваться" }}

</button>

</form>

<div class="login-link">

Уже есть аккаунт?

<router-link to="/login">
Войти
</router-link>

</div>

</div>

</div>

</template>

<style scoped>

.register-page{

display:flex;
justify-content:center;

padding:40px;

}

.register-card{

width:100%;
max-width:600px;

background:white;

padding:30px;

border-radius:12px;

box-shadow:0 10px 30px rgba(0,0,0,0.1);

}

.title{

text-align:center;
margin-bottom:20px;

}

form{

display:flex;
flex-direction:column;
gap:12px;

}

input,
select,
textarea{

padding:10px;

border:1px solid #ddd;

border-radius:6px;

}

h3{

margin-top:20px;

}

.avatar-upload{

display:flex;
flex-direction:column;
gap:10px;

}

.avatar-preview{

width:120px;
height:120px;

border-radius:50%;

overflow:hidden;

background:#eee;

display:flex;
align-items:center;
justify-content:center;

}

.avatar-preview img{

width:100%;
height:100%;
object-fit:cover;

}

.avatar-placeholder{

font-size:40px;

}

.btn-register{

margin-top:20px;

padding:12px;

border:none;

background:#4a76a8;
color:white;

border-radius:8px;

font-size:16px;

cursor:pointer;

}

.error{

background:#ffe5e5;

padding:10px;

margin-bottom:10px;

border-radius:6px;

color:#b00000;

}

.login-link{

margin-top:20px;

text-align:center;

}

</style>