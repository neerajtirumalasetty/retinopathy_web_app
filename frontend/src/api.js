import axios from "axios";

// Change this if your FastAPI backend runs on a different host/port.
export const API_BASE_URL = "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

/**
 * Sends the retinal image + patient details to the backend and returns
 * the prediction result.
 *
 * @param {File} imageFile - the uploaded retinal fundus image
 * @param {Object} patientDetails - { age, gender, diabetic_history, symptoms }
 * @param {string} language - language code for the generated explanation ("en" | "hi" | "te")
 */
export async function predictRetinopathy(imageFile, patientDetails, language = "en") {
  const formData = new FormData();
  formData.append("file", imageFile);

  if (patientDetails.age !== "" && patientDetails.age !== null) {
    formData.append("age", patientDetails.age);
  }
  if (patientDetails.gender) {
    formData.append("gender", patientDetails.gender);
  }
  if (patientDetails.diabetic_history) {
    formData.append("diabetic_history", patientDetails.diabetic_history);
  }
  if (patientDetails.symptoms) {
    formData.append("symptoms", patientDetails.symptoms);
  }
  formData.append("language", language);

  const response = await apiClient.post("/api/predict", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return response.data;
}

export async function checkHealth() {
  const response = await apiClient.get("/health");
  return response.data;
}

export default apiClient;
