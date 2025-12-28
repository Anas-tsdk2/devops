// router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../views/HomePage.vue';
import NewQuizPage from '../views/NewQuizPage.vue';
import QuestionsManager from '../components/QuestionsManager.vue';
import LoginPage from '../views/LoginPage.vue';
import ResultPage from '../views/ResultPage.vue';
import AdminPage from '@/views/AdminPage.vue';
import QuestionEdition from '@/components/QuestionEdition.vue';
import QuestionAdminDisplay from '@/components/QuestionAdminDisplay.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
    },
    {
      path: '/new-quiz',
      name: 'new-quiz',
      component: NewQuizPage,
    },
    {
      path: '/questions',
      name: 'questions',
      component: QuestionsManager,
    },
    { path: '/result',
      name: 'result',
      component: ResultPage
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminPage,
    },
    {
      path: '/edition',
      name: 'edition',
      component: QuestionEdition,
    },
    {
      path: '/question-admin',
      name: 'question-admin',
      component: QuestionAdminDisplay,
    },
  ],
});

export default router;
