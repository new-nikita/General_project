<script setup lang="ts">
import { ref } from "vue"
import { useUserStore } from "@/stores/userStore"

const emit = defineEmits<{
  (e: "new-post", post: any): void
}>()

const content = ref("")
const userStore = useUserStore()

const submitPost = async () => {
  if (!content.value.trim()) return
  const newPost = await userStore.createPost({ content: content.value })
  emit("new-post", newPost)
  content.value = ""
}
</script>

<template>
  <div class="post-form card p-3 mb-4">
    <textarea v-model="content" class="form-control mb-2" placeholder="Что у вас нового?" rows="3"></textarea>
    <button class="btn btn-primary" @click="submitPost">Опубликовать</button>
  </div>
</template>

<style scoped>
.post-form textarea {
  resize: none;
}
</style>