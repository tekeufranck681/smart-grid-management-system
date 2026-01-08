import api from "../config/axiosConfigGridImport";

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

export const gridImportService = {
  importGridFromFile: async (workspaceId, file) => {
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await api.post(`/grids/${workspaceId}`, formData);
      return response.data;
    } catch (error) {
      normalizeError(error, "Grid import failed");
    }
  },
};
