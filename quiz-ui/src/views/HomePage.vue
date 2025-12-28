<!-- views/HomePage.vue -->
<script setup>
import { ref, onMounted } from 'vue';
import QuizApiService from '@/services/QuizApiService';

const topScores = ref([]); // [{ playerName, score }, ...]

onMounted(async () => {
  const res = await QuizApiService.getQuizInfo();
  const all = res?.data?.scores ?? [];
  topScores.value = all.slice(0, 3); // top 3 déjà triés côté back
});
</script>

<template>
  <div class="wrapper double">
    <div class="launch-quiz">
      <h1 class="big-title">Testez vos connaissances</h1>
      <router-link to="/new-quiz" class="button launch-btn">Démarrer le quiz !</router-link>
    </div>
    <div>
      <img src="../assets/fonds/t-rex.jpg" class="quiz-img home-img"/>
    </div>
  </div>

  <div class="wrapper scoreboard" >
    <div>
      <h1 class="title">Meilleurs scores</h1>
      <div class="wrapper triple classement">
        <div class="right-text yellow">
          <p v-for="(s, i) in topScores" :key="i">{{ i + 1 }}</p>
        </div>
        <div class="center-text">
          <p v-if="!topScores.length" class="empty">Aucun score pour le moment.</p>
          <p v-for="(s, i) in topScores" :key="i">{{ s.playerName }}</p>
        </div>
        <div class="left-text green">
          <p v-for="(s, i) in topScores" :key="i">{{ s.score }}</p>
        </div>
      </div>
    </div>
    <div></div>
  </div>
</template>
