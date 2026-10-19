<script setup lang="ts">
const authStore = useAuthStore()

// Initialize auth state on app startup (Universal - Server & Client)
authStore.init()
</script>

<template>
  <div>
    <NuxtPwaManifest />
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>

<style>
/* Global styles */
body {
  font-family: 'Inter', sans-serif;
  margin: 0;
  padding: 0;
}

.card-shadow {
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
}
</style>
