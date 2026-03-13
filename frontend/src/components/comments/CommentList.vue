<script setup lang="ts">
import { ref, onMounted } from "vue"
import axios from "axios"
import CommentItem from "./CommentItem.vue"
import CommentForm from "./CommentForm.vue"

const props = defineProps({
  postId: Number
})

const comments = ref([])

const loadComments = async () => {
  const res = await axios.get(`/posts/${props.postId}/comments`)
  comments.value = res.data
}

const addComment = (comment) => {
  comments.value.push(comment)
}

const removeComment = (id) => {
  comments.value = comments.value.filter(c => c.id !== id)
}

onMounted(loadComments)
</script>

<template>
  <div class="comments-section">

    <CommentForm
      :postId="postId"
      @comment-added="addComment"
    />

    <div v-if="comments.length">

      <CommentItem
        v-for="comment in comments"
        :key="comment.id"
        :comment="comment"
        @deleted="removeComment"
      />

    </div>

    <div v-else class="text-muted small mt-2">
      Пока нет комментариев
    </div>

  </div>
</template>