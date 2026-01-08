import axios from "axios";
import { useAuthStore } from "../stores/authStore";

const GRID_EDGE_BASE_URL = `${process.env.NEXT_PUBLIC_WORKSPACEGRID_URL}/grids`;

const api = axios.create({
  baseURL: GRID_EDGE_BASE_URL,
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
});

let isRefreshing = false;
let refreshPromise = null;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { logout, refreshToken, isAuthenticated } =
      useAuthStore.getState();
    const status = error.response?.status;

    if (status === 401 && isAuthenticated) {
      const isRefreshEndpoint = error.config?.url?.includes("/refresh-token");
      if (!isRefreshEndpoint) {
        if (!isRefreshing) {
          isRefreshing = true;
          refreshPromise = refreshToken().finally(() => {
            isRefreshing = false;
            refreshPromise = null;
          });
        }
        return refreshPromise
          .then(() => api.request(error.config))
          .catch(() => {
            logout();
            return Promise.reject(error);
          });
      }
    }

    return Promise.reject(error);
  }
);

export default api;
