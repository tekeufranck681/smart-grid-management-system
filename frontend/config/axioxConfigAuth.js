// src/config/axiosConfigAuth.js
import axios from "axios";
import { useAuthStore } from "../stores/authStore";

const AUTH_BASE_URL = `${process.env.NEXT_PUBLIC_BACKEND_URL}/auth`;

const api = axios.create({
  baseURL: AUTH_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true, // send cookies automatically
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { logout, refreshToken, isAuthenticated } = useAuthStore.getState();
    const status = error.response?.status;

    if (status === 401 && isAuthenticated) {
      const isLoginEndpoint = error.config?.url?.includes("/login");
      const isLogoutEndpoint = error.config?.url?.includes("/logout");
      const isRefreshEndpoint = error.config?.url?.includes("/refresh-token");
      const isValidateEndpoint = error.config?.url?.includes("/verify-token");
      if (!isLoginEndpoint && !isLogoutEndpoint && !isRefreshEndpoint && !isValidateEndpoint) {
        // Try refresh token
        try {
          await refreshToken();
          // If refresh succeeds, retry the original request
          return api.request(error.config);
        } catch {
          // If refresh fails, logout
          logout();
        }
      }
    }

    return Promise.reject(error);
  }
);

export default api;
