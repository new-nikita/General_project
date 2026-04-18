<script setup lang="ts">
import { ref, onMounted, watch } from "vue"
import { useRoute } from "vue-router"
import { useUserStore } from "@/stores/userStore"
import ProfileHeader from "@/components/users/ProfileHeader.vue"
import ProfileModals from "@/components/users/ProfileModals.vue"
import PostList from "@/components/users/PostList.vue"
import PostCreate from "@/components/posts/PostCreate.vue"

const route = useRoute()
const userStore = useUserStore()

const user = ref(null)
const posts = ref([])
const isOwnProfile = ref(false)
const loading = ref(true)

const profileModal = ref()

const loadProfile = async () => {
  loading.value = true

  const userId = Number(route.params.id)

  const res = await userStore.fetchProfile(userId)

  user.value = res.user
  posts.value = res.posts
  isOwnProfile.value = res.is_own_profile

  loading.value = false
}

onMounted(loadProfile)
watch(() => route.params.id, loadProfile)
</script>

<template>
  <div class="profile-page">

    <!-- ПРОФИЛЬ -->
    <div class="block">
      <ProfileHeader
        v-if="user"
        :user="user"
        :isOwnProfile="isOwnProfile"
        :isAuthenticated="true"
        :isFriend="user?.is_friend"
        @show-info="profileModal?.openProfile()"
      />

      <div v-else class="placeholder">
        Загрузка профиля...
      </div>
    </div>

    <ProfileModals ref="profileModal" :user="user" />

    <!-- СОЗДАТЬ ПОСТ -->
    <div class="block" v-if="isOwnProfile && user">
      <PostCreate @post-created="posts.unshift($event)" />
    </div>

    <!-- ПОСТЫ -->
    <div class="block">

      <div v-if="loading" class="placeholder">
        Загрузка постов...
      </div>

      <PostList v-else-if="posts.length" :posts="posts" />

      <div v-else class="empty">
        Постов пока нет
      </div>

    </div>

  </div>
</template>

<style scoped>
.profile-page{
  display:flex;
  flex-direction:column;
  gap:15px;
}

.block{
  background:white;
  border-radius:12px;
  padding:15px;
  box-shadow:0 1px 3px rgba(0,0,0,0.08);
}

.placeholder{
  text-align:center;
  color:#818c99;
  padding:20px;
}

.empty{
  text-align:center;
  color:#818c99;
  padding:30px;
}
</style>