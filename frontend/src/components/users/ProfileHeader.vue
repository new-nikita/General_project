<script setup lang="ts">
import { ref } from "vue"
import axios from "axios"

const props = defineProps({
  user: Object,
  isOwnProfile: Boolean,
  isAuthenticated: Boolean,
  isFriend: Boolean
})

const emit = defineEmits(["show-info"])

const friend = ref(props.isFriend)

const addFriend = async () => {
  try {

    await axios.post("/friends/add", {
      user_id: props.user.id
    })

    friend.value = true

  } catch (e) {
    console.error("Friend add error", e)
  }
}
</script>

<template>

<div class="d-flex align-items-center mb-4 profile-header">

  <!-- AVATAR -->

  <div class="profile-avatar me-4">
    <img
      :src="user.profile.avatar"
      alt="Аватар"
      class="user-avatar rounded-circle shadow-sm"
    >
  </div>

  <div class="profile-details flex-grow-1">

    <!-- NAME -->

    <h3
      v-if="user.profile.first_name || user.profile.last_name"
      class="text-muted mb-2"
    >
      {{ user.profile.first_name || "" }}
      {{ user.profile.last_name || "" }}
    </h3>

    <!-- EMAIL -->

    <p
      v-if="isOwnProfile && user.email"
      class="text-muted mb-3"
    >
      <i class="fas fa-envelope me-1"></i>
      {{ user.email }}
    </p>

    <!-- ACTION BUTTONS -->

    <div class="profile-actions d-flex gap-2 mt-2 mb-3">

      <!-- INFO -->

      <button
        class="btn btn-outline-primary btn-sm flex-grow-1"
        @click="$emit('show-info')"
      >
        <i class="fas fa-info-circle me-1"></i>
        Подробнее
      </button>

      <!-- EDIT PROFILE -->

      <a
        v-if="isOwnProfile"
        :href="`/profile/edit/${user.id}`"
        class="btn btn-outline-secondary btn-sm"
      >
        <i class="fas fa-user-edit me-1"></i>
        Редактировать
      </a>

      <!-- FRIEND BUTTON -->

      <button
        v-else-if="isAuthenticated && friend"
        class="btn btn-success btn-sm"
        disabled
      >
        <i class="fas fa-user-check me-1"></i>
        В друзьях
      </button>

      <button
        v-else-if="isAuthenticated"
        class="btn btn-primary btn-sm"
        @click="addFriend"
      >
        <i class="fas fa-user-plus me-1"></i>
        В друзья
      </button>

    </div>

    <!-- MESSAGE BUTTON -->

    <div
      v-if="!isOwnProfile && isAuthenticated"
      class="w-100"
    >

      <a
        :href="`/ws/chat/dialog/${user.id}`"
        class="btn btn-outline-success btn-sm w-100 py-2"
      >
        <i class="fas fa-comment me-2"></i>
        Написать сообщение
      </a>

    </div>

  </div>

</div>

</template>