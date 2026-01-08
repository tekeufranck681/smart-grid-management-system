import api from "../config/axiosConfigGrid";

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

export const gridService = {
  createGrid: async (workspaceId, payload) => {
    try {
      const response = await api.post(
        `/workspaces/${workspaceId}/grids`,
        payload
      );
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to create grid");
    }
  },

  listGridsForWorkspace: async (workspaceId) => {
    try {
      const response = await api.get(
        `/workspaces/${workspaceId}/grids`
      );
      return response.data.grids;
    } catch (error) {
      normalizeError(error, "Failed to fetch grids");
    }
  },

  getGridById: async (gridId) => {
    try {
      const response = await api.get(`/${gridId}`);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to fetch grid");
    }
  },

  updateGrid: async (gridId, payload) => {
    try {
      const response = await api.put(`/${gridId}`, payload);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to update grid");
    }
  },

  deleteGrid: async (gridId) => {
    try {
      const response = await api.delete(`/${gridId}`);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to delete grid");
    }
  },
};
