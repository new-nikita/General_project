<script setup lang="ts">

defineProps<{
  message:{
    text:string
    is_self:boolean
  }
}>()

</script>

<template>

<div
class="message"
:class="{self:message.is_self}"
>

{{ message.text }}

</div>

</template>

<style scoped>

.message{

max-width:70%;

padding:10px 14px;

border-radius:20px;

margin-bottom:10px;

background:#eee;

}

.self{

margin-left:auto;

background:#4a76a8;
color:white;

}

</style>