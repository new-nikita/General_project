<script setup lang="ts">
import { ref } from "vue"
import axios from "axios"

const emit = defineEmits(["post-created"])

const showForm = ref(false)
const content = ref("")
const image = ref<File | null>(null)
const loading = ref(false)

const toggleForm = () => {
  showForm.value = !showForm.value
}

const handleFile = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files) {
    image.value = target.files[0]
  }
}

const submitPost = async () => {

  if (!content.value.trim() && !image.value) return

  const form = new FormData()
  form.append("content", content.value)

  if (image.value) {
    form.append("image", image.value)
  }

  loading.value = true

  try {

    const res = await axios.post("/posts/create", form)

    emit("post-created", res.data)

    content.value = ""
    image.value = null
    showForm.value = false

  } catch (e) {
    console.error("Post create error", e)
  } finally {
    loading.value = false
  }
}
</script>

<template>

<!-- КНОПКА СОЗДАНИЯ -->

<button
  class="btn-toggle-post-form d-flex align-items-center justify-content-center"
  @click="toggleForm"
>
  <i class="fas fa-plus me-2"></i>
  Создать новый пост
</button>

<!-- ФОРМА -->

<div v-if="showForm" class="add-post-block mt-3">

  <div class="mb-3">
    <textarea
      v-model="content"
      class="form-control"
      rows="3"
      placeholder="Что у вас нового?"
    ></textarea>
  </div>

  <div class="mb-3">
    <input
      class="form-control"
      type="file"
      accept="image/*"
      @change="handleFile"
    >
  </div>

  <button
    class="btn btn-publish"
    :disabled="loading"
    @click="submitPost"
  >
    <i class="fas fa-paper-plane me-2"></i>
    Опубликовать
  </button>

</div>

</template>