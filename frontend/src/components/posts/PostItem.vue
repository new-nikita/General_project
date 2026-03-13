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

const toggleLike = async () => {
  try {
    if (liked.value) {
      await axios.post(`/posts/${props.post.id}/unlike`)
      likesCount.value--
    } else {
      await axios.post(`/posts/${props.post.id}/like`)
      likesCount.value++
    }

    liked.value = !liked.value
  } catch (e) {
    console.error("Like error", e)
  }
}

const deletePost = async () => {
  if (!confirm("Удалить пост?")) return

  await axios.delete(`/posts/${props.post.id}`)

  const el = document.getElementById(`post-${props.post.id}`)
  if (el) el.remove()
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

const showComments = ref(false)

</script>

<template>
  <div class="post-item" :id="'post-' + post.id">

    <!-- HEADER -->

    <div class="post-header">
      <img
        :src="post.author.profile.avatar"
        class="post-author-avatar"
      />

      <span class="post-author">
        {{ post.author.profile.full_name || post.author.username }}
      </span>
    </div>

    <!-- IMAGE -->

    <div v-if="post.image" class="post-image-container">
      <img :src="post.image" class="post-image">
    </div>

    <!-- CONTENT -->

    <div v-if="!editing && post.content" class="post-content">
      {{ post.content }}
    </div>

    <!-- EDIT FORM -->

    <div v-if="editing" class="edit-post-form mt-2">

      <textarea
        v-model="content"
        class="form-control mb-2"
        rows="3"
      ></textarea>

      <input
        type="file"
        class="form-control mb-2"
        accept="image/*"
        @change="e => image = e.target.files[0]"
      >

      <button
        class="btn btn-sm btn-primary"
        @click="saveEdit"
      >
        Сохранить
      </button>


    </div>

    <!-- ACTIONS -->

    <div class="post-actions d-flex">

      <!-- LIKE -->

      <div class="like-container">
        <button
          class="like-button"
          :class="{ liked: liked }"
          @click="toggleLike"
        >
          <i :class="liked ? 'fas fa-heart' : 'far fa-heart'"></i>

          <span v-if="likesCount > 0" class="like-counter">
            {{ likesCount }}
          </span>
        </button>
      </div>

      <!-- EDIT -->

      <button
        v-if="post.author_id === currentUserId"
        class="post-action-btn edit-post-btn"
        @click="editing = !editing"
      >
        <i class="far fa-edit"></i> Редактировать
      </button>

      <!-- DELETE -->

      <button
        v-if="isOwn"
        class="delete-post-btn text-danger"
        @click="deletePost"
      >
        Удалить
      </button>

    </div>

    <!-- DATE -->

    <div class="post-date">
      {{ new Date(post.created_at).toLocaleString() }}
    </div>

    <button @click="showComments = !showComments">
    💬 Комментарии
    </button>

    <CommentList v-if="showComments" :postId="post.id" />

    <!-- COMMENTS -->

    <div class="comments-section"></div>

  </div>
</template>

<style scoped>

.post-item {
  background: white;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 20px;
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

.post-image {
  width: 100%;
  border-radius: 10px;
  margin-top: 10px;
}

.like-button {
  border: none;
  background: none;
  cursor: pointer;
}

.like-button.liked i {
  color: red;
}

.post-date {
  font-size: 12px;
  color: gray;
  margin-top: 10px;
}

</style>