<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import { useUserStore } from "@/stores/userStore"
import ProfileHeader from "@/components/users/ProfileHeader.vue"
import ProfileModals from "@/components/users/ProfileModals.vue"
import PostForm from "@/components/users/PostForm.vue"
import PostList from "@/components/users/PostList.vue"
import PostCreate from "@/components/posts/PostCreate.vue";

const route = useRoute()
const userStore = useUserStore()
const userId = Number(route.params.id)

const user = ref(null)
const posts = ref([])
const isOwnProfile = ref(false)

const profileModal = ref()

onMounted(async () => {
  const data = await userStore.fetchProfile(userId)
  user.value = data.user
  posts.value = data.posts
  isOwnProfile.value = data.isOwnProfile
})
</script>

<template>
  <div class="profile-container">
    <ProfileHeader
      :user="user"
      :isOwnProfile="isOwnProfile"
      :isAuthenticated="true"
      :isFriend="user.is_friend"
      @show-info="profileModal.openProfile()"
    />
    <ProfileModals ref="profileModal" :user="user" />

    <PostCreate
      v-if="isOwnProfile"
      @post-created="posts.unshift($event)"
    />

    <PostList :posts="posts" />
  </div>
</template>

<style scoped>
.profile-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
}
</style>