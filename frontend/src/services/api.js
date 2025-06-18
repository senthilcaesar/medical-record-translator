import axios from "axios";

const API_BASE_URL = "/api/v1";

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// API service methods
export const translationAPI = {
  // Upload a document for translation
  uploadDocument: async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/translate/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  },

  // Get the status of a translation job
  getJobStatus: async (jobId) => {
    const response = await api.get(`/translate/status/${jobId}`);
    return response.data;
  },

  // Get the translation result
  getTranslationResult: async (jobId) => {
    const response = await api.get(`/translate/result/${jobId}`);
    return response.data;
  },

  // Delete a job
  deleteJob: async (jobId) => {
    const response = await api.delete(`/translate/job/${jobId}`);
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get("/translate/health");
    return response.data;
  },
};

// Helper function to poll job status
export const pollJobStatus = async (jobId, onProgress, onComplete, onError) => {
  const maxAttempts = 300; // 300 attempts = 1 minute with 200ms intervals
  let attempts = 0;

  const poll = async () => {
    try {
      const status = await translationAPI.getJobStatus(jobId);

      if (status.status === "completed") {
        const result = await translationAPI.getTranslationResult(jobId);
        onComplete(result);
        return;
      }

      if (status.status === "failed") {
        onError(new Error(status.error || "Translation failed"));
        return;
      }

      // Update progress
      if (onProgress) {
        onProgress(status);
      }

      // Continue polling if still processing (any non-terminal state)
      const processingStates = [
        "processing",
        "extracting_text",
        "identifying_document_type",
        "translating",
      ];
      if (processingStates.includes(status.status) && attempts < maxAttempts) {
        attempts++;

        setTimeout(poll, 200); // Poll every 200ms for smoother progress updates
      } else if (attempts >= maxAttempts) {
        onError(new Error("Translation timeout - please try again"));
      }
    } catch (error) {
      onError(error);
    }
  };

  // Start polling
  poll();
};

export default api;
