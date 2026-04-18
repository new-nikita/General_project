<template>
  <div class="layout">

    <Header @toggle-sidebar="sidebarOpen = !sidebarOpen" />

    <Sidebar :open="sidebarOpen" />

    <main class="content">
      <router-view />
    </main>

  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import Header from "@/components/layout/Header.vue"
import Sidebar from "@/components/layout/Sidebar.vue"

const sidebarOpen = ref(false)
</script>

<style scoped>

.layout{
  background:#edeef0;
  min-height:100vh;
}

/* центральная колонка как в VK */
.content{
  margin-top:60px;
  margin-left:260px;

  padding:20px;

  max-width:700px;
}

/* мобильная адаптация */
@media (max-width:992px){

  .content{
    margin-left:0;
    padding:15px;
  }

}

</style>