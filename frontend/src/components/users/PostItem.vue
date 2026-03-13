<script setup lang="ts">
import { ref } from "vue"
import { useUserStore } from "@/stores/userStore"

const props = defineProps<{ post: any }>()
const userStore = useUserStore()

const liked = ref(props.post.liked)
const likesCount = ref(props.post.likesCount)

const toggleLike = async () => {
  if (liked.value) {
    await userStore.unlikePost(props.post.id)
    likesCount.value--
  } else {
    await userStore.likePost(props.post.id)
    likesCount.value++
  }
  liked.value = !liked.value
}
</script>

<template>
  <div class="post-item card mb-3">
    <div class="card-body">
      <p>{{ post.content }}</p>
      <div class="d-flex justify-content-between align-items-center mt-2">
        <button class="btn btn-sm" @click="toggleLike">
          <i :class="liked ? 'fas fa-heart text-danger' : 'far fa-heart'"></i>
          {{ likesCount }}
        </button>
      </div>
    </div>
  </div>
</template>