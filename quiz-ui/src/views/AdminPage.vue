<!-- src/views/AdminPage.vue -->
<template>
  <div class="admin">
    <!-- Login si pas de token -->
    <div v-if="!token" class="login">
      <h2 class="title">Administration</h2>
      <input
        type="password"
        v-model="password"
        placeholder="Mot de passe"
        @keyup.enter="login"
      />
      <button @click="login" class="button">Connexion</button>
      <p v-if="loginError" class="error">Mauvais mot de passe</p>
    </div>

    <!-- Contenu admin si token présent -->
    <div v-else>
      <header class="topbar">
        <h2>Admininistration</h2>

      </header>

      <section class="content">
        <QuestionsList />
      </section>
      <button class="button" @click="logout">Déconnexion</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import QuestionsList from "@/components/QuestionsList.vue";
import QuizApiService from "@/services/QuizApiService";

const token = ref(localStorage.getItem("adminToken") || "");
const password = ref("");
const loginError = ref(false);

async function login() {
  loginError.value = false;
  const res = await QuizApiService.call("post", "/login", { password: password.value });
  if (res && res.status === 200 && res.data?.token) {
    token.value = res.data.token;
    localStorage.setItem("adminToken", token.value);
    password.value = "";
  } else {
    loginError.value = true;
  }
}

function logout() {
  token.value = "";
  console.log("Logging out", token.value);
  localStorage.removeItem("adminToken");
  location.href = "/";
}
</script>

