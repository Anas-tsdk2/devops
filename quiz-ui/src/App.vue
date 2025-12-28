<script setup>
import { /*RouterLink,*/ RouterView } from 'vue-router'
import navbar from "./views/Navbar.vue";
</script>

<template>
  <div class="background">
    <navbar/>

    <RouterView />
  </div>
</template>