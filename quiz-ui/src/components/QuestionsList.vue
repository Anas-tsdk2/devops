<!-- components/QuestionsList.vue -->
<template>
  <div class="list">
    <h2>Liste des questions</h2>

    <router-link class="btn" to="/edition">Créer une question</router-link>

    <ul class="items" v-if="questions && questions.length">
      <li v-for="q in questions" :key="q.id">
        <router-link :to="{ name: 'question-admin', query: { id: q.id } }">
          <strong>#{{ q.position }}</strong> — {{ q.title }}
        </router-link>
      </li>
    </ul>

    <p v-else>Aucune question pour le moment.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import QuizApiService from "@/services/QuizApiService";

const questions = ref([]);

onMounted(async () => {
  // récupérer le nombre total de questions
  const info = await QuizApiService.getQuizInfo();
  const size = info?.data?.size ?? 0;
  if (!size) return;

  //charger chaque question par position (1..size)
  for (let pos = 1; pos <= size; pos++) {
    const res = await QuizApiService.getQuestion(pos);
    if (res?.status === 200 && res.data) {
      questions.value.push(res.data);
    }
  }
});
</script>

<style scoped>
.list {
  max-width: 720px;
  margin: 24px auto;
  padding: 16px;
}
.btn {
  display: inline-block;
  margin: 8px 0 16px;
  padding: 10px 14px;
  border-radius: 40px;
  /*background: #eef2ff;*/
  background-color: var(--second-color);
  color: #1f2937;
  text-decoration: none;
  font-weight: 600;
}
.items { list-style: none; padding: 0; margin: 0; }
.items li { padding: 10px 0; border-bottom: 1px solid #eee; }
.items a { text-decoration: none; color: #c1a724; font-weight: 600; }
</style>
