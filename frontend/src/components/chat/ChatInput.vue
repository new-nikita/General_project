<script setup lang="ts">
import { ref } from "vue"

const emit = defineEmits(["send"])

const text = ref("")

function submit() {

  if (!text.value.trim()) return

  emit("send", text.value)

  text.value = ""

}
</script>

<template>

<form class="chat-input" @submit.prevent="submit">

<input
v-model="text"
placeholder="Введите сообщение..."
/>

<button>
Отправить
</button>

</form>

</template>

<style scoped>

.chat-input{
display:flex;
gap:10px;
padding:10px;
}

input{
flex:1;
padding:10px;
border-radius:20px;
border:1px solid #ccc;
}

button{
padding:10px 20px;
border:none;
background:#4a76a8;
color:white;
border-radius:20px;
}

</style>