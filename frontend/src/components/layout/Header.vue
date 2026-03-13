<script setup lang="ts">
import { useAuthStore } from "@/stores/authStore"

const auth = useAuthStore()

defineEmits(["toggle-sidebar"])
</script>

<template>
<header class="header">

<div class="left">

<button class="mobile-menu"
        @click="$emit('toggle-sidebar')">
☰
</button>

<router-link to="/" class="logo">
МояВКонтакте
</router-link>

<button class="back" @click="$router.back()">
←
</button>

</div>

<div class="right">

<router-link
v-if="auth.user"
:to="`/profile/${auth.user.id}`"
>
Профиль
</router-link>

<button v-if="auth.user" @click="auth.logout()">
Выйти
</button>

<router-link v-if="!auth.user" to="/login">
Войти
</router-link>

<router-link v-if="!auth.user" to="/register">
Регистрация
</router-link>

</div>

</header>
</template>

<style scoped>

.header{
position:fixed;
top:0;
left:0;
right:0;
height:60px;

display:flex;
justify-content:space-between;
align-items:center;

padding:0 20px;

background:#4a76a8;
color:white;
}

.logo{
color:white;
text-decoration:none;
font-weight:600;
}

.mobile-menu{
display:none;
}

@media (max-width:992px){

.mobile-menu{
display:block;
}

}

</style>