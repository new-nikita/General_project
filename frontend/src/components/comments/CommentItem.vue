<script setup lang="ts">
import axios from "axios"

const props = defineProps({
  comment: Object
})

const emit = defineEmits(["deleted"])

const deleteComment = async () => {
  if (!confirm("Удалить комментарий?")) return

  await axios.delete(`/comments/${props.comment.id}`)

  emit("deleted", props.comment.id)
}
</script>

<template>
  <div class="comment-item">

    <img
      :src="comment.author.profile.avatar"
      class="comment-avatar"
    />

    <div class="comment-body">

      <div class="comment-header">

        <span class="comment-author">
          {{ comment.author.profile.full_name || comment.author.username }}
        </span>

        <span class="comment-date">
          {{ new Date(comment.created_at).toLocaleString() }}
        </span>

      </div>

      <div class="comment-text">
        {{ comment.content }}
      </div>

      <button
        v-if="comment.can_delete"
        class="comment-delete"
        @click="deleteComment"
      >
        удалить
      </button>

    </div>

  </div>
</template>

<style scoped>

.comment-item{
display:flex;
gap:10px;
margin-top:10px;
}

.comment-avatar{
width:32px;
height:32px;
border-radius:50%;
}

.comment-body{
flex:1;
}

.comment-header{
display:flex;
gap:10px;
font-size:13px;
}

.comment-author{
font-weight:600;
}

.comment-date{
color:gray;
font-size:12px;
}

.comment-text{
margin-top:4px;
}

.comment-delete{
background:none;
border:none;
color:red;
font-size:12px;
cursor:pointer;
}

</style>