<template>
<header class="header">

  <div class="left">

    <button class="mobile-menu" @click="$emit('toggle-sidebar')">
      ☰
    </button>

    <router-link to="/" class="logo">
      МояВКонтакте
    </router-link>

    <button class="back" @click="router.back()">
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

<script setup lang="ts">
import { useAuthStore } from "@/stores/authStore"
import { useRouter } from "vue-router"

const auth = useAuthStore()
const router = useRouter()

defineEmits(["toggle-sidebar"])
</script>

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

  box-shadow:0 2px 8px rgba(0,0,0,0.1);
  z-index:1000;
}

.logo{
  color:white;
  text-decoration:none;
  font-weight:600;
}

.mobile-menu{
  display:none;
  margin-right:10px;
}

.left{
  display:flex;
  align-items:center;
}

.right{
  display:flex;
  align-items:center;
}

.right a,
.right button{
  margin-left:15px;
  color:white;
  text-decoration:none;
  font-size:14px;
}

.right button{
  background:none;
  border:none;
  cursor:pointer;
}

@media (max-width:992px){
  .mobile-menu{
    display:block;
  }
}
</style>