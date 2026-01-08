import api from "../config/axioxConfigAuth";

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

export const authService = {
  register: async (user) => {
    try {
      const response = await api.post("/register", user);
      return response.data;
    } catch (error) {

      normalizeError(error, "Registration failed");

    }
  },

  login: async (credentials) => {
    try {
      const response = await api.post("/login", credentials);
      return response.data.data;
    } catch (error) {
      normalizeError(error, "Login failed");
    }
  },

  validateToken: async () => {
    try {
      const response = await api.post("/verify-token"); // cookie sent automatically
      const user = response.data.data;
      return user;
    } catch (error) {
      normalizeError(error, "Token validation failed");
    }
  },

  logout: async () => {
    try {
      await api.post("/logout"); // backend clears cookies
      return { message: "Logged out successfully" };
    } catch (error) {
      normalizeError(error, "Logout failed");
    }
  },

  forgotPassword: async (email) => {
    try {
      const response = await api.post("/forgot-password", { email });
      return response.data;
    } catch (error) {
      normalizeError(error, "Forgot password failed");
    }
  },

  resetPassword: async ({ token, new_password }) => {
    try {
      const response = await api.post("/reset-password", { token, new_password });
      return response.data;
    } catch (error) {
      normalizeError(error, "Reset password failed");
    }
  },

  verifyEmail: async (token) => {
    try {
      const response = await api.post("/verify-email", { token });
      return response.data;
    } catch (error) {
      normalizeError(error, "Email verification failed");
    }
  },

  resendVerification: async (email) => {
    try {
      const response = await api.post("/resend-verification", { email });
      return response.data;
    } catch (error) {
      normalizeError(error, "Resend verification failed");
    }
  },

  refreshToken: async () => {
    try {
      const response = await api.post("/refresh-token");
      return response.data;
    } catch (error) {
      normalizeError(error, "Refresh token failed");
    }
  },
};
