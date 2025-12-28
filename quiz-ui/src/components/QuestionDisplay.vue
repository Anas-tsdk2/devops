<!-- components/QuestionDisplay-->
<template>
  <div v-if="question" class="wrapper double">
    <div>
      <p class="question__title">{{ question.title }}</p>
      <p class="question__text">{{ question.text }}</p>
      <div class="wrapper answers">
        <a class="button" @click="emit('click-on-answer', 1)">
          {{ question.possibleAnswers[0].text }}
        </a>
        <a class="button" @click="emit('click-on-answer', 2)">
          {{ question.possibleAnswers[1].text }}
        </a>
        <a class="button" @click="emit('click-on-answer', 3)">
          {{ question.possibleAnswers[2].text }}
        </a>
        <a class="button" @click="emit('click-on-answer', 4)">
          {{ question.possibleAnswers[3].text }}
        </a>
      </div>
    </div>
    <div>
      <img v-if="question.image" :src="question.image" alt="Chargement de l'image..." class="quiz-img"/>
    </div>
  </div>
</template>

<script setup>
defineProps({
  question: Object
});
const emit = defineEmits(['click-on-answer']);
</script>

<style scoped>

.question {
  max-width: 720px;
  margin: 24px auto;
  padding: 16px;
  text-align: center;
}

.question__title {
  margin: 0 0 8px;
  font-size: 1.6rem;
  color: rgb(180, 180, 180);
  font-weight: lighter;
}

.question__text {
  margin: 0 0 16px;
  font-size: 2.5rem;
  color: #fbfdfd;
  font-weight: 700;
}

.question__image {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,.08);
  margin: 12px 0 20px;
}

/* 2 réponses par ligne */
.answers {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 70px;
}

.answers .button {
  transition: .3s ease;
  cursor: pointer;
  padding: 25px;
  border-radius: 100px;
  font-size: 1.4rem;
  margin: 40px 20px;
}

.answers .button:hover {
  transform: translateY(-5px);
  background-color: transparent;
  color: var(--second-color);
  box-shadow: 0 0 10px var(--second-color);
}

.answers .button:active {
  transform: translateY(0);
}

/* ajustement mobile */
@media (max-width: 480px) {
  .answers {
    grid-template-columns: 1fr; /* une par ligne si l'écran est trop étroit */
  }
}
</style>
