<template>
  <div class="result">
    <h1>Résultat</h1>
    <div class="classement">

      <p class="player">
        Joueur : <strong>{{ playerName }}</strong>
      </p>
      <p class="score">
        Score : <strong>{{ currentScore }}</strong> / {{ totalQuestions }}
      </p>

      <div class="ranking" v-if="totalParticipants > 0">
        <p>Classement : <strong>{{ playerRank }}</strong> / {{ totalParticipants }}</p>
      </div>
    </div>

    <div class="wrapper double scoreboard">
      <!-- Bloc scores généraux -->
      <div>
        <h1 class="title">Scores généraux</h1>

        <div class="wrapper triple classement">
          <div class="right-text yellow">
            <p
              v-for="(entry, index) in topScores"
              :key="'rank-' + index"
            >
              {{ index + 1 }}
            </p>
          </div>

          <div class="center-text">
            <p
              v-for="(entry, index) in topScores"
              :key="'name-' + index"
            >
              {{ entry.playerName }}
            </p>
          </div>

          <div class="left-text green">
            <p
              v-for="(entry, index) in topScores"
              :key="'score-' + index"
            >
              {{ entry.score }}
            </p>
          </div>
        </div>

        <p v-if="!topScores.length" class="empty">
          Aucun score pour le moment.
        </p>
      </div>

      <!-- Bloc score personnel -->
      <div>
        <h1 class="title">Scores personnels</h1>

        <div class="wrapper triple classement" v-if="totalParticipants">
          <div class="right-text yellow">
            <p>{{ playerRank }}</p>
          </div>
          <div class="center-text">
            <p>{{ playerName }}</p>
          </div>
          <div class="left-text green">
            <p>{{ currentScore }}</p>
          </div>
        </div>

        <p v-else class="empty">Aucune participation enregistrée.</p>
      </div>
    </div>
    <router-link to="/" class="button">Retour à l'accueil</router-link>

  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import ParticipationStorageService from "@/services/ParticipationStorageService";
import QuizApiService from "@/services/QuizApiService";

const playerName = ref("");
const currentScore = ref(0);
const totalQuestions = ref(0);

const totalParticipants = ref(0);
const playerRank = ref(null);
const topScores = ref([]); // Tableau d'objets: [{ playerName, score }]


function getSafeInteger(value, fallback = 0) {
  const parsed = parseInt(value, 10);
  return Number.isNaN(parsed) ? fallback : parsed;
}

function computeRank(scores, name, score) {
  // Tente de trouver la position exacte du couple (name, score)
  const exactIndex = scores.findIndex(
    (participant) =>
      participant.playerName === name && Number(participant.score) === score
  );

  if (exactIndex !== -1) {
    return exactIndex + 1; // index base 0 -> rang base 1
  }

  // Sinon, rang = nombre de scores strictement supérieurs + 1
  const betterScoresCount = scores.filter(
    (participant) => Number(participant.score) > score
  ).length;

  return betterScoresCount + 1;
}


onMounted(async () => {
  // Récupère le nom et le score enregistrés côté client
  playerName.value = ParticipationStorageService.getPlayerName() || "Unknown";
  currentScore.value = getSafeInteger(
    ParticipationStorageService.getParticipationScore(),
    0
  );

  const quizInfoResponse = await QuizApiService.getQuizInfo();
  const quizInfo = quizInfoResponse?.data ?? {};

  totalQuestions.value = quizInfo.size ?? 0;

  const allScores = Array.isArray(quizInfo.scores) ? quizInfo.scores : [];
  totalParticipants.value = allScores.length;

  // Top 3
  topScores.value = allScores.slice(0, 3);

  // Rang du joueur courant
  playerRank.value = computeRank(
    allScores,
    playerName.value,
    currentScore.value
  );
});
</script>

<style scoped>
.result {
  min-height: 60vh;
  max-width: 680px;
  margin: 0 auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.player,
.score,
.done {
  margin: 6px 0;
  font-size: 1.1rem;
}

.ranking {
  margin: 10px 0 4px;
}

.home-btn {
  margin-top: 18px;
  padding: 10px 14px;
  border-radius: 10px;
  background: #eef2ff;
  border: 1px solid #dbe1ff;
  color: #1f2937;
  text-decoration: none;
  font-weight: 600;
}


</style>
