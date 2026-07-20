<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useThemeStore } from './stores/theme'

const auth = useAuthStore()
const themeStore = useThemeStore()

onMounted(() => {
  themeStore.initTheme()
  if (auth.isLoggedIn) {
    auth.fetchUser()
  }
})
</script>
