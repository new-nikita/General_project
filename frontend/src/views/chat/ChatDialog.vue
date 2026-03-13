<script setup lang="ts">
import { onMounted, onUnmounted } from "vue"
import { useRoute } from "vue-router"

import { useChatSocket } from "@/composables/useChatSocket"
import { useChatStore } from "@/stores/chatStore"

import ChatMessage from "@/components/chat/ChatMessage.vue"
import ChatInput from "@/components/chat/ChatInput.vue"

const route = useRoute()
const store = useChatStore()

const dialogId = Number(route.params.id)

const { send, disconnect } = useChatSocket(dialogId)

onUnmounted(() => {
  disconnect()
})

</script>

<template>

<div class="chat">

<div class="chat-status">

<span v-if="store.connected" class="online">
● подключено
</span>

<span v-else class="offline">
● переподключение...
</span>

</div>

<div class="messages">

<ChatMessage
v-for="(msg,i) in store.messages"
:key="i"
:message="msg"
/>

</div>

<ChatInput @send="send" />

</div>

</template>

<style scoped>

.chat{
max-width:700px;
margin:0 auto;

display:flex;
flex-direction:column;

height:80vh;
}

.messages{
flex:1;
overflow:auto;
padding:10px;
}

.chat-status{
font-size:12px;
margin-bottom:10px;
}

.online{
color:green;
}

.offline{
color:red;
}

</style>