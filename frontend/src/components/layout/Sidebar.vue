<script setup lang="ts">
import { useAuthStore } from "@/stores/authStore"

const auth = useAuthStore()

defineProps<{
  open:boolean
}>()
</script>

<template>

<aside class="sidebar" :class="{open}">

<ul>

<li v-if="auth.user">
<router-link :to="`/profile/${auth.user.id}`">
Моя страница
</router-link>
</li>

<li>
<router-link to="/friends">
Друзья
</router-link>
</li>

<li>
<router-link to="/messages">
Сообщения
</router-link>
</li>

<li>
<router-link to="/news">
Новости
</router-link>
</li>

</ul>

</aside>

</template>

<style scoped>

.sidebar{

width:250px;
background:white;

position:fixed;

top:60px;
bottom:0;
left:0;

transform:translateX(0);
transition:0.3s;

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
