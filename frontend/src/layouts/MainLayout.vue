<template>
  <div>
    <header>Header</header>
    <main>
      <router-view></router-view>
    </main>
    <footer>Footer</footer>
  </div>
</template>

<script lang="ts">
export default {}
</script>

<style scoped>
header, footer { background: #eee; padding: 1rem; }
main { padding: 2rem; }
</style>