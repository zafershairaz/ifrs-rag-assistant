import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const askQuestion = async (question) => {
  const response = await api.post("/ask", {
    question: question,
  });

  return response.data;
};