import api from "../config/axiosConfigGridNode";

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

export const gridNodeService = {
  createNode: async (gridId, nodeData) => {
    try {
      const response = await api.post(`/${gridId}/nodes/`, nodeData);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to create node");
    }
  },

  getNode: async (gridId, nodeId) => {
    try {
      const response = await api.get(`/${gridId}/nodes/${nodeId}`);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to fetch node");
    }
  },

  updateNode: async (gridId, nodeId, nodeData) => {
    try {
      const response = await api.put(`/${gridId}/nodes/${nodeId}`, nodeData);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to update node");
    }
  },

  updateNodePosition: async (gridId, nodeId, positionData) => {
    try {
      const response = await api.patch(
        `/${gridId}/nodes/${nodeId}/position`,
        positionData
      );
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to update node position");
    }
  },

  deleteNode: async (gridId, nodeId) => {
    try {
      const response = await api.delete(`/${gridId}/nodes/${nodeId}`);
      return response.data;
    } catch (error) {
      normalizeError(error, "Failed to delete node");
    }
  },
};
