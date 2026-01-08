import api from "../config/axiosConfigScenario";

const normalizeError = (error, fallbackMessage) => {
  const message =
    error.response?.data?.detail ||
    error.response?.data?.message ||
    error.message ||
    fallbackMessage;
  const status = error.response?.status;
  const err = new Error(message);
  err.status = status;
  throw err;
};

export const scenarioService = {
  createScenario: async (gridId, scenarioData) => {
    try {
      const response = await api.post(`/${gridId}`, scenarioData);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to create scenario");
    }
  },

  addScenarioEvent: async (scenarioId, eventData) => {
    try {
      const response = await api.post(`/${scenarioId}/events`, eventData);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to add scenario event");
    }
  },

  listScenariosByGrid: async (gridId) => {
    try {
      const response = await api.get(`/${gridId}/list`);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to list scenarios");
    }
  },

  getScenario: async (scenarioId) => {
    try {
      const response = await api.get(`/${scenarioId}`);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to fetch scenario");
    }
  },

  updateScenarioStatus: async (scenarioId, newStatus) => {
    try {
      const response = await api.patch(`/${scenarioId}/status`, {
        new_status: newStatus,
      });
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to update scenario status");
    }
  },

  deleteScenario: async (scenarioId) => {
    try {
      const response = await api.delete(`/${scenarioId}`);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to delete scenario");
    }
  },
};
