<script setup lang="ts">
import { ref } from "vue"

const props = defineProps({
  user: Object
})

const showProfile = ref(false)
const showAvatar = ref(false)

const openProfile = () => {
  showProfile.value = true
}

const closeProfile = () => {
  showProfile.value = false
}

const openAvatar = () => {
  showAvatar.value = true
}

const closeAvatar = () => {
  showAvatar.value = false
}

defineExpose({
  openProfile
})
</script>

<template>

<!-- PROFILE INFO MODAL -->

<div v-if="showProfile" class="profile-modal">

  <span class="close-modal" @click="closeProfile">
    &times;
  </span>

  <div class="user-info">

    <!-- BASIC INFO -->

    <div class="info-section">

      <h4>
        <i class="fas fa-info-circle"></i>
        Основная информация
      </h4>

      <div
        v-if="user.profile.birth_date"
        class="info-item"
      >
        <span class="info-label">
          Дата рождения:
        </span>

        <span class="info-value">
          {{ new Date(user.profile.birth_date).toLocaleDateString() }}
        </span>
      </div>

      <div
        v-if="user.profile.gender"
        class="info-item"
      >
        <span class="info-label">
          Пол:
        </span>

        <span class="info-value">
          {{ user.profile.gender }}
        </span>
      </div>

    </div>

    <!-- BIO -->

    <div
      v-if="user.profile.bio"
      class="info-section"
    >

      <h4>
        <i class="fas fa-quote-left"></i>
        О себе
      </h4>

      <div style="white-space: pre-line;">
        {{ user.profile.bio }}
      </div>

    </div>

  </div>

</div>

<!-- OVERLAY -->

<div
  v-if="showProfile || showAvatar"
  class="modal-overlay"
  @click="closeProfile"
></div>

<!-- AVATAR FULLSCREEN -->

<div
  v-if="showAvatar"
  class="fullscreen-view"
>

  <span
    class="close-fullscreen"
    @click="closeAvatar"
  >
    &times;
  </span>

  <img
    :src="user.profile.avatar"
    class="fullscreen-avatar"
  >

</div>

</template>