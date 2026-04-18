<template>
<aside class="sidebar" :class="{open}">

  <ul>

    <li v-if="auth.user">
      <router-link :to="`/profile/${auth.user.id}`">
        Моя страница
      </router-link>
    </li>

    <li>
      <router-link to="/friends">Друзья</router-link>
    </li>

    <li>
      <router-link to="/messages">Сообщения</router-link>
    </li>

    <li>
      <router-link to="/news">Новости</router-link>
    </li>

  </ul>

</aside>
</template>

<script setup lang="ts">
import { useAuthStore } from "@/stores/authStore"

const auth = useAuthStore()

defineProps<{
  open:boolean
}>()
</script>

<style scoped>
.sidebar{
  width:260px;
  background:#fff;

  position:fixed;
  top:60px;
  bottom:0;
  left:0;

  padding:15px;

  border-right:1px solid #e7e8ec;

  transition:0.3s;
}

.sidebar ul{
  list-style:none;
  padding:0;
}

.sidebar li{
  margin-bottom:10px;
}

.sidebar a{
  display:block;
  text-decoration:none;
  color:#2a5885;
  font-weight:500;
  padding:6px 10px;
  border-radius:6px;
}

.sidebar a:hover{
  background:#f0f2f5;
}

@media (max-width:992px){

  .sidebar{
    transform:translateX(-100%);
  }

  .sidebar.open{
    transform:translateX(0);
  }

}
</style>