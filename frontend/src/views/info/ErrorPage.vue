<script setup lang="ts">
</script>

<template>

<div class="error-page">

  <div class="card">

    <i class="fas fa-exclamation-triangle icon"></i>

    <h2>Что-то пошло не так</h2>

    <p>
      Возникла ошибка при выполнении вашего запроса.
      Попробуйте позже.
    </p>

    <router-link to="/" class="btn">
      Вернуться на главную
    </router-link>

  </div>

</div>

</template>

<style scoped>

.error-page {
  display: flex;
  justify-content: center;
  margin-top: 80px;
}

.card {
  padding: 40px;
  text-align: center;
  background: white;
  border-radius: 10px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.1);
}

.icon {
  font-size: 48px;
  color: red;
  margin-bottom: 20px;
}

.btn {
  margin-top: 20px;
  background: #4a76a8;
  color: white;
  padding: 10px 20px;
  border-radius: 6px;
}

</style>