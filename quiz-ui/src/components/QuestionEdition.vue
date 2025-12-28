<!-- QuestionEdition.vue -->
<template>
  <!-- Afficher uniquement si token présent -->
  <div v-if="token">
    <div class="wrap" v-if="local">
      <h2>Éditer la question</h2>

      <label class="row">
        <span>Position</span>
        <input type="number" v-model.number="local.position" min="1" />
      </label>

      <label class="row">
        <span>Titre</span>
        <input type="text" v-model="local.title" />
      </label>

      <label class="row">
        <span>Intitulé</span>
        <textarea v-model="local.text" rows="3"></textarea>
      </label>

      <div class="row">
        <span>Image</span>
        <div class="col">
          <ImageUpload
            :fileDataUrl="imageAsb64"
            @file-change="imageFileChangedHandler"
          />
          <img v-if="local.image" :src="local.image" alt="aperçu" class="preview" />
        </div>
      </div>

      <div class="answers">
        <div class="answer" v-for="(ans, i) in local.possibleAnswers" :key="i">
          <label class="row">
            <span>Réponse {{ i + 1 }}</span>
            <input type="text" v-model="ans.text" />
          </label>
          <label class="row">
            <input type="checkbox" :checked="ans.isCorrect" @change="setCorrect(i)" />
            <span>Bonne réponse</span>
          </label>
        </div>
      </div>

      <div class="actions">
        <button @click="onCancel" class="button2">Annuler</button>
        <button @click="onSave" class="button">Enregistrer</button>
      </div>
    </div>
  </div>

  <!-- Si pas de token -->
  <div v-else class="denied">
    Accès réservé. Veuillez vous connecter.
  </div>
  <button class="button" @click="logout">Déconnexion</button>
</template>

<script setup>
import { ref, onMounted, watchEffect } from "vue";
import { useRoute, useRouter } from "vue-router";
import QuizApiService from "@/services/QuizApiService";
import ImageUpload from "@/components/ImageUpload.vue";

const props = defineProps({ question: Object });

const router = useRouter();
const route = useRoute();

const token = ref(localStorage.getItem("adminToken") || "");

function makeEmpty() {
  return {
    id: null,
    position: 1,
    title: "",
    text: "",
    image: null,
    possibleAnswers: [
      { text: "", isCorrect: false },
      { text: "", isCorrect: false },
      { text: "", isCorrect: false },
      { text: "", isCorrect: false },
    ],
  };
}

const local = ref(null);
const imageAsb64 = ref("");

// copie locale depuis props (si fournie)
watchEffect(() => {
  if (props.question) {
    const copy = JSON.parse(JSON.stringify(props.question));
    while (copy.possibleAnswers.length < 4)
      copy.possibleAnswers.push({ text: "", isCorrect: false });
    if (copy.possibleAnswers.length > 4)
      copy.possibleAnswers = copy.possibleAnswers.slice(0, 4);
    local.value = copy;
    imageAsb64.value = copy.image || "";
  }
});

// chargement par id route si pas de props
onMounted(async () => {
  if (!token.value) return; // pas de token on n'affiche pas l'édition
  if (!local.value) {
    const id = route.params.id || route.query.id;
    if (id) {
      const res = await QuizApiService.call("get", `/questions/${id}`);
      if (res?.status === 200) {
        const copy = JSON.parse(JSON.stringify(res.data));
        while (copy.possibleAnswers.length < 4)
          copy.possibleAnswers.push({ text: "", isCorrect: false });
        if (copy.possibleAnswers.length > 4)
          copy.possibleAnswers = copy.possibleAnswers.slice(0, 4);
        local.value = copy;
        imageAsb64.value = copy.image || "";
      } else {
        local.value = makeEmpty();
        imageAsb64.value = "";
      }
    } else {
      local.value = makeEmpty();
      imageAsb64.value = "";
    }
  }
});

// upload image → maj base64
function imageFileChangedHandler(b64String) {
  imageAsb64.value = b64String || "";
  if (local.value) local.value.image = imageAsb64.value;
}

function setCorrect(index) {
  local.value.possibleAnswers.forEach((a, i) => (a.isCorrect = i === index));
}

async function onSave() {
  const payload = {
    title: local.value.title,
    text: local.value.text,
    image: local.value.image,
    position: local.value.position,
    possibleAnswers: local.value.possibleAnswers.map((a) => ({
      text: a.text,
      isCorrect: !!a.isCorrect,
    })),
  };

  const auth = token.value || null;

  if (local.value.id) {
    await QuizApiService.call("put", `/questions/${local.value.id}`, payload, auth);
  } else {
    await QuizApiService.call("post", "/questions", payload, auth);
  }
  router.back();
}

function onCancel() {
  router.back();
}

function logout() {
  localStorage.removeItem("adminToken");
  token.value = "";
  router.push("/admin");
}
</script>

<style scoped>
.wrap { max-width: 800px; margin: 24px auto; padding: 16px; }
.row { display: flex; align-items: center; gap: 12px; margin: 8px 0; }
.row > span { width: 120px; font-weight: 600; }
.row input[type="text"], .row input[type="number"], .row textarea { flex: 1; padding: 8px; }
.col { display: flex; flex-direction: column; gap: 8px; }
.preview { max-width: 320px; border-radius: 8px; }
.answers { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-top: 12px; }
.answer { border: 1px solid #eee; border-radius: 8px; padding: 12px; }
.actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }

/* Bouton déconnexion  */
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

.denied { text-align: center; margin: 80px 0; }
</style>
