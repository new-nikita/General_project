<script setup lang="ts">
import { onMounted, ref } from "vue"
import { useRouter } from "vue-router"

interface Dialog {
  user_id: number
  username: string
  last_message: string
}

const router = useRouter()

const dialogs = ref<Dialog[]>([])
const loading = ref(true)

function openDialog(id: number) {
  router.push(`/chat/${id}`)
}

async function loadDialogs() {
  try {
    const response = await fetch("/api/messages/dialogs")
    const data = await response.json()

    dialogs.value = data
  } catch (e) {
    console.error("Ошибка загрузки диалогов", e)
  } finally {
    loading.value = false
  }
}

onMounted(loadDialogs)
</script>

<template>
<div class="dialogs-page">

<h1 class="title">Сообщения</h1>

<div v-if="loading" class="loading">
Загрузка...
</div>

<div v-else-if="dialogs.length === 0" class="empty">
У вас пока нет диалогов
</div>

<div v-else class="dialogs-list">

<div
v-for="dialog in dialogs"
:key="dialog.user_id"
class="dialog-item"
@click="openDialog(dialog.user_id)"
>

<div class="avatar">
{{ dialog.username[0] }}
</div>

<div class="dialog-info">

<div class="username">
{{ dialog.username }}
</div>

<div class="last-message">
{{ dialog.last_message }}
</div>

</div>

</div>

</div>

</div>
</template>

<style scoped>

.dialogs-page{
max-width:700px;
margin:0 auto;
}

.title{
margin-bottom:20px;
}

.loading,
.empty{
text-align:center;
color:#777;
}

.dialogs-list{
display:flex;
flex-direction:column;
gap:10px;
}

.dialog-item{

display:flex;
align-items:center;

padding:12px;

background:white;
border-radius:10px;

cursor:pointer;
transition:0.2s;

}

.dialog-item:hover{
background:#f1f1f1;
}

.avatar{

width:40px;
height:40px;

border-radius:50%;

background:#4a76a8;
color:white;

display:flex;
align-items:center;
justify-content:center;

font-weight:bold;
margin-right:12px;

}

.username{
font-weight:600;
}

.last-message{
font-size:14px;
color:#777;
}

</style>