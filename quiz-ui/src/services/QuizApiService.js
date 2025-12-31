// services/QuizApiService.js

import axios from "axios";

const instance = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000
});

export default {
  async call(method, resource, data = null, token = null, params = null) {
    var headers = {
      "Content-Type": "application/json",
    };
    if (token != null) {
      headers.authorization = "Bearer " + token;
    }

    return instance({
      method,
      headers,
      url: resource.startsWith("/") ? resource : `/${resource}`,
      data: ["post","put","patch"].includes(method.toLowerCase()) ? data : undefined,
      params
    })
      .then((response) => {
        return { status: response.status, data: response.data };
      })
      .catch((error) => {
        console.error(error);
      });
  },

  getQuizInfo() {
    return this.call("get", "/quiz-info");
  },

  getQuestion(position) {
    return this.call("get", "/questions", null, null, { position });
  },

  postParticipation(payload) {
    return this.call("post", "/participations", payload);
  },

  getAllQuestions() {
  return this.call("get", "/questions/all");
}

};
