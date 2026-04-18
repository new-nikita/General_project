<template>
  <div class="post-item" :id="'post-' + post.id">

    <div class="post-header">
      <img :src="post.author.profile.avatar" class="post-author-avatar" />

      <span class="post-author">
        {{ post.author.profile.full_name || post.author.username }}
      </span>
    </div>

    <div v-if="post.image" class="post-image-container">
      <img :src="post.image" class="post-image">
    </div>

    <div v-if="!editing && post.content" class="post-content">
      {{ post.content }}
    </div>

    <div v-if="editing" class="edit-post-form">
      <textarea v-model="content" rows="3"></textarea>

      <input type="file" @change="e => image = e.target.files[0]" />

      <button @click="saveEdit">Сохранить</button>
    </div>

    <div class="post-actions">

      <button
        class="like-button"
        :class="{ liked: liked }"
        @click="toggleLike"
      >
        ❤️ {{ likesCount }}
      </button>

      <button
        v-if="post.author_id === currentUserId"
        @click="editing = !editing"
      >
        Редактировать
      </button>

      <button
        v-if="isOwn"
        class="delete"
        @click="deletePost"
      >
        Удалить
      </button>

    </div>

    <div class="post-date">
      {{ new Date(post.created_at).toLocaleString() }}
    </div>

    <button class="comments-toggle" @click="showComments = !showComments">
      💬 Комментарии
    </button>

    <CommentList v-if="showComments" :postId="post.id" />

  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import axios from "axios"
import CommentList from "@/components/comments/CommentList.vue"

const props = defineProps({
  post: Object,
  currentUserId: Number,
  isOwn: Boolean
})

const editing = ref(false)

const liked = ref(props.post.is_liked_by_current)
const likesCount = ref(props.post.likes_count)

const content = ref(props.post.content)
const image = ref(null)

const showComments = ref(false)

const toggleLike = async () => {
  if (liked.value) {
    await axios.post(`/posts/${props.post.id}/unlike`)
    likesCount.value--
  } else {
    await axios.post(`/posts/${props.post.id}/like`)
    likesCount.value++
  }

  liked.value = !liked.value
}

const deletePost = async () => {
  if (!confirm("Удалить пост?")) return
  await axios.delete(`/posts/${props.post.id}`)
  document.getElementById(`post-${props.post.id}`)?.remove()
}

const saveEdit = async () => {
  const form = new FormData()
  form.append("content", content.value)

  if (image.value) {
    form.append("image", image.value)
  }

  await axios.post(`/posts/${props.post.id}/edit`, form)
  editing.value = false
}
</script>

<style scoped>
.post-item {
  background: white;
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 15px;

  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

.post-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.post-author-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.post-author {
  font-weight:600;
  color:#2a5885;
}

.post-content{
  margin-top:10px;
}

.post-image {
  width: 100%;
  border-radius: 10px;
  margin-top: 10px;
}

.post-actions{
  display:flex;
  gap:10px;
  margin-top:10px;
}

.like-button{
  background:none;
  border:none;
  cursor:pointer;
}

.like-button.liked{
  color:#e64646;
}

.delete{
  color:red;
}

.post-date {
  font-size: 12px;
  color: #818c99;
  margin-top: 8px;
}

.comments-toggle{
  margin-top:10px;
  background:none;
  border:none;
  color:#2a5885;
  cursor:pointer;
}
</style>