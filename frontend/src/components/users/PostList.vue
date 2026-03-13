<script setup lang="ts">
import PostItem from "./PostItem.vue"
const props = defineProps<{ posts: any[] }>()
</script>

<template>
  <div class="post-list">
    <template v-if="posts.length">
      <PostItem v-for="post in posts" :key="post.id" :post="post" />
    </template>
    <div v-else class="no-posts text-center text-muted py-4">
      <i class="far fa-newspaper fa-2x mb-2"></i>
      <p>Постов пока нет</p>
    </div>
  </div>
</template>