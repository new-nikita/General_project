<script setup lang="ts">
import { ref } from "vue"
import axios from "axios"

const props = defineProps({
  postId: Number
})

const emit = defineEmits(["comment-added"])

const content = ref("")
const loading = ref(false)

const submit = async () => {

  if (!content.value.trim()) return

  loading.value = true

  try{

    const res = await axios.post(`/posts/${props.postId}/comments`, {
      content: content.value
    })

    emit("comment-added", res.data)

    content.value = ""

  }finally{
    loading.value = false
  }

}
</script>

<template>

<div class="comment-form">

  <textarea
    v-model="content"
    placeholder="Написать комментарий..."
    class="form-control"
    rows="2"
  ></textarea>

  <button
    class="btn btn-sm btn-primary mt-1"
    :disabled="loading"
    @click="submit"
  >
    Отправить
  </button>

</div>

</template>

<style scoped>

.comment-form{
margin-top:10px;
}

textarea{
resize:none;
}

</style>