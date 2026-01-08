import api from "../config/axiosConfigWorkspace";

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

export const workspaceService = {
  createWorkspace: async (payload) => {
    try {
      const response = await api.post("/", payload);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to create workspace");
    }
  },

  listWorkspaces: async () => {
    try {
      const response = await api.get("/");
      return response.data.workspaces;
    } catch (error) {
      normalizeError(error, "Failed to fetch workspaces");
    }
  },

  getWorkspaceById: async (workspaceId) => {
    try {
      const response = await api.get(`/${workspaceId}`);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to fetch workspace");
    }
  },

  updateWorkspace: async (workspaceId, payload) => {
    try {
      const response = await api.put(`/${workspaceId}`, payload);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to update workspace");
    }
  },

  deleteWorkspace: async (workspaceId) => {
    try {
      const response = await api.delete(`/${workspaceId}`);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to delete workspace");
    }
  },
};
