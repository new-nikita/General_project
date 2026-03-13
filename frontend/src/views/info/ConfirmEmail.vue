<template>
  <div class="confirm-page">
    <div class="confirm-card">
      <div class="icon">
        <i class="fas fa-envelope-open-text"></i>
      </div>

      <h2>Почти готово!</h2>

      <p>
        Мы отправили письмо с подтверждением на указанный вами адрес электронной почты.
        <br />
        Пожалуйста, перейдите по ссылке в письме, чтобы завершить регистрацию.
      </p>

      <hr />

      <p class="small text-muted">
        Если вы не получили письмо в течение нескольких минут, проверьте папку «Спам» или
        <router-link to="/resend-confirmation" class="text-primary">запросите повторную отправку</router-link>.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
// Пока логика resend не добавляем, просто отображение
</script>

<style scoped>
.confirm-page {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.confirm-card {
  max-width: 480px;
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 5px 25px rgba(0,0,0,0.08);
  text-align: center;
}

.icon {
  font-size: 50px;
  color: #4a76a8;
  margin-bottom: 20px;
}

h2 {
  margin-bottom: 15px;
}

p {
  color: #555;
  line-height: 1.5;
}

hr {
  margin: 20px 0;
  border: 0;
  border-top: 1px solid #eee;
}

.text-primary {
  color: #4a76a8;
  text-decoration: none;
}
</style>