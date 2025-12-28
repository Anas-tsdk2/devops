<!-- components/QuestionAdminDisplay.vue -->
<template>
  <!-- Afficher seulement si token présent -->
  <div v-if="token">
    <div class="wrap" v-if="question">
      <div class="actions">
        <button @click="onCancel" class="editer">Retour</button>
        <button @click="goEdit" class="editer">Éditer</button>
        <button class="danger" @click="deleteQuestion">Supprimer</button>
      </div>

      <h2 class="title">{{ question.title }}</h2>
      <p class="text">{{ question.text }}</p>
      <img v-if="question.image" :src="question.image" alt="" class="image" />

      <ul class="answers">
        <li v-for="ans in question.possibleAnswers" :key="ans.id ?? ans.index">
          <label>
            <input type="radio" :checked="ans.isCorrect" disabled />
            <span>{{ ans.text }}</span>
          </label>
        </li>
      </ul>
    </div>

    <p v-else class="empty">Chargement…</p>

    <button class="button" @click="logout">Déconnexion</button>
  </div>

  <!-- Si pas de token -->
  <div v-else class="empty">
    Accès réservé. Veuillez vous connecter.
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import QuizApiService from "@/services/QuizApiService";

const route = useRoute();
const router = useRouter();

const token = ref(localStorage.getItem("adminToken") || "");
const question = ref(null);

onMounted(async () => {
  if (!token.value) return; // pas de token on n’affiche pas la page
  const id = route.params.id || route.query.id;
  if (!id) return;
  const res = await QuizApiService.call("get", `/questions/${id}`);
  if (res?.status === 200) question.value = res.data;
});

function goEdit() {
  if (!question.value) return;
  router.push({ path: "/edition", query: { id: question.value.id } });
}

async function deleteQuestion() {
  if (!question.value) return;
  if (!confirm("Supprimer cette question ?")) return;

  const res = await QuizApiService.call("delete", `/questions/${question.value.id}`, null, token.value );
  if (res && (res.status === 200 || res.status === 204)) {
    router.push("/admin");
  }
}

function onCancel() {
  router.push('/admin');
}

function logout() {
  localStorage.removeItem("adminToken");
  token.value = "";
  router.push("/admin");
}
</script>

<style scoped>
.wrap {
  max-width: 720px;
  margin: 24px auto;
  padding: 16px;
  text-align: center;
}

.actions { display: flex; gap: 15px; justify-content: flex-end; margin-bottom: 30px; }
.danger { background: #f05050; border: 1px solid #ec5353; border-radius: 40px; padding: 10px 20px; }
.editer { background-color: var(--second-color); border-radius: 40px; width: 110px; border: none; }

.title {
  margin: 0 0 8px;
  font-size: 1.5rem;
  color: #f3f33e;
  font-weight: 700;
}
.text {
  margin: 0 0 16px;
  font-size: 2rem;
  color: #fbfdfd;
  font-weight: 700;
}

.image {
  max-height: 600px;
  width: 700px;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,.08);
  margin: 12px 0 20px;
}

.answers {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  justify-items: center;
}
.answers li { width: 100%; }
.answers li label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 12px 14px;
  border-radius: 10px;
  background: #f5f7fb;
  border: 1px solid #e5e8ef;
  color: #1f2937;
  font-weight: 600;
  transition: transform .06s ease, box-shadow .06s ease, background .2s;
  box-shadow: 0 1px 3px rgba(0,0,0,.05);
}
.answers li label:hover {
  background: #bfe17a;
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(0,0,0,.08);
}

/* Chargement / accès refusé */
.empty { text-align: center; margin: 24px 0; }

/* Bouton déconnexion */
.logout-fixed {
  position: fixed;
  left: 16px;
  bottom: 16px;
  padding: 10px 14px;
  border-radius: 10px;
  background: #fee2e2;
  border: 1px solid #fecaca;
  color: #7f1d1d;
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 480px) {
  .answers { grid-template-columns: 1fr; }
}
</style>
