import axios from "axios";

// Vite injects this at build time from .env.development or .env.production.
const API_BASE_URL = import.meta.env.VITE_API_URL;

export const analyzeTicket = async (ticketText) => {
  const response = await axios.post(`${API_BASE_URL}/analyze-ticket`, {
    text: ticketText,
  });
  return response.data;
};

export const transcribeAudio = async (audioBlob) => {
  const formData = new FormData();
  // The backend uses the filename to infer audio format. MediaRecorder
  // produces webm by default in Chromium/Firefox.
  formData.append("audio", audioBlob, "recording.webm");

  const response = await axios.post(
    `${API_BASE_URL}/transcribe-audio`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
  return response.data.transcript;
};
