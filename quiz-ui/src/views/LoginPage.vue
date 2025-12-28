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
  <div class="new-quiz block">
    <h1>Connexion</h1>
    <p>Identifiant </p>
    <div class="input-group mb-3">
      <div class="input-group-prepend">
        <span class="input-group-text" id="basic-addon1">@</span>
        </div>
        <input type="text" class="form-control" placeholder="Identifiant" aria-label="Identifiant" aria-describedby="basic-addon1" v-model="id">
        <button type="button" class="btn btn-primary" @click="launchNewQuiz">GO!</button>
    </div>
    <p>Mot de passe </p>
    <div class="input-group mb-3">
      <div class="input-group-prepend">
        <span class="input-group-text" id="basic-addon1">@</span>
        </div>
        <input type="text" class="form-control" placeholder="Mot de passe" aria-label="Mot-de-passe" aria-describedby="basic-addon1" v-model="mdp">
        <button type="button" class="btn btn-primary" @click="launchNewQuiz">GO!</button>
    </div>
  </div>
</template>

<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style>


