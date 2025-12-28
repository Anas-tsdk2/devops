<script setup>
    import { ref} from 'vue';
    import { useRouter } from 'vue-router';
    import participationStorageService from "@/services/ParticipationStorageService";

    const router = useRouter();

    const username = ref('');
    function launchNewQuiz() {
      console.log("Launch new quiz with", username.value);
      participationStorageService.savePlayerName(username.value);
      router.push('/questions');
    }

</script>

<template>
  <div class="new-quiz">
    <div v-if="!token" class="login">
      <h2 class="title">Saisissez votre nom</h2>
      <input
        type="text"
        v-model="username"
        placeholder="Username"
        aria-label="Username"
      />
      <button @click="launchNewQuiz" class="button">GO !</button>
    </div>
  </div>
</template>


