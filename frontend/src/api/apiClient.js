import axios from "axios";

const API_BASE_URL = "https://support-ai-backend-497667180395.us-central1.run.app";

export const analyzeTicket = async (ticketText) => {
  const response = await axios.post(`${API_BASE_URL}/analyze-ticket`, {
    text: ticketText,
  });

  return response.data;
};