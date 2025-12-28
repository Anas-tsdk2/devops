<!-- components/QuestionsManager-->
<template>
  <h1 class="title">Question {{ currentQuestionPosition }} / {{ totalNumberOfQuestion }}</h1>
  <QuestionDisplay
    v-if="currentQuestion"
    :question="currentQuestion"
    @click-on-answer="answerClickedHandler"
  />
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import QuestionDisplay from "../components/QuestionDisplay.vue";
import QuizApiService from "@/services/QuizApiService";
import ParticipationStorageService from "@/services/ParticipationStorageService";

const router = useRouter();

const currentQuestionPosition = ref(1);           // <-- 1-based
const totalNumberOfQuestion = ref(0);
const currentQuestion = ref(null);
const selectedAnswer = ref([]);                    // indices 1..4

onMounted(async () => {
  const playerName = ParticipationStorageService.getPlayerName();
  if (!playerName) {
    router.push("/new-quiz");
    return;
  }

  const info = await QuizApiService.getQuizInfo();
  totalNumberOfQuestion.value = info.data.size;

  if (totalNumberOfQuestion.value > 0) {
    await loadQuestionByPosition(currentQuestionPosition.value);
  }
});

async function loadQuestionByPosition(pos) {
  const response = await QuizApiService.getQuestion(pos); // /questions?position=pos
  currentQuestion.value = (response && response.data) ? response.data : null;
}

async function answerClickedHandler(choiceIndex) {
  selectedAnswer.value.push(choiceIndex);

  const nextPos = currentQuestionPosition.value + 1;
  if (nextPos > totalNumberOfQuestion.value) {
    await endQuiz();
  } else {
    currentQuestionPosition.value = nextPos;
    await loadQuestionByPosition(nextPos);
  }
}

async function endQuiz() {
  const player = {
    playerName: ParticipationStorageService.getPlayerName(),
    answers: selectedAnswer.value,
  };

  const response = await QuizApiService.postParticipation(player);
  ParticipationStorageService.saveParticipationScore(response.data.score);
  router.push("/result");
}
</script>
