<script setup>
import { onMounted } from 'vue';

onMounted(async () => {
  console.log('Nav mounted');
});

</script>

<template>
    <nav id="nav">
        <div class="flex navbar">
            <router-link to="/"><img src="../assets/logos/q-blanc.png" class="logo-navbar"></router-link>
            <div>
                <router-link to="/" class="button home-btn">Home</router-link>
                <router-link to="/admin" class="button">Admin</router-link>
            </div>
        </div>
    </nav>
</template>

<style>
nav {
    min-width: fit-content;
    margin: 0 0 25px 0;
    min-height: 50px;
}

.navbar {
    gap: 40px;
    padding: 1% 0 0 2%;
    flex-direction: row;
}

.logo-navbar {
    width: 70px;
    height: 70px;
    min-width: 70px;
    min-height: 70px;
    margin: 20px;
}

nav .button {
    margin: 50px 70px 50px 0;
}
</style>
