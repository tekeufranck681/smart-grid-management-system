import api from "../config/axiosConfigGridEdge";

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

export const gridEdgeService = {
  createEdge: async (gridId, edgeData) => {
    try {
      const response = await api.post(`/${gridId}/edges/`, edgeData);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to create edge");
    }
  },

  getEdge: async (gridId, edgeId) => {
    try {
      const response = await api.get(`/${gridId}/edges/${edgeId}`);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to fetch edge");
    }
  },

  updateEdge: async (gridId, edgeId, edgeData) => {
    try {
      const response = await api.put(`/${gridId}/edges/${edgeId}`, edgeData);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to update edge");
    }
  },

  updateEdgeState: async (gridId, edgeId, stateData) => {
    try {
      const response = await api.patch(
        `/${gridId}/edges/${edgeId}/state`,
        stateData
      );
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to update edge state");
    }
  },

  deleteEdge: async (gridId, edgeId) => {
    try {
      const response = await api.delete(`/${gridId}/edges/${edgeId}`);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to delete edge");
    }
  },
};
