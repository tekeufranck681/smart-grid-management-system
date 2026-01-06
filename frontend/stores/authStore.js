import { create } from "zustand";
import { authService } from "../services/authService";

export const useAuthStore = create((set, get) => ({
  // Global user/auth state
  user: null,
  isAuthenticated: false,
  isAuthLoading: false,
  error: null,

  // Per-action loading states
  loginLoading: false,
  registerLoading: false,
  forgotPasswordLoading: false,
  resetPasswordLoading: false,
  verifyEmailLoading: false,
  resendVerificationLoading: false,

  // Messages for one-off actions
  forgotPasswordMessage: null,
  resetPasswordMessage: null,
  registerMessage: null,
  verifyEmailMessage: null,
  resendVerificationMessage: null,

  // Core user actions
  login: async (credentials) => {
    set({ loginLoading: true, error: null });
    try {
      const user = await authService.login(credentials);
      set({ user, isAuthenticated: true, loginLoading: false, error: null });
      return user;
    } catch (error) {
      set({ loginLoading: false, error: error.message });
      throw error;
    }
  },

  logout: async () => {
    try {
      await authService.logout();
    } finally {
      set({
        user: null,
        isAuthenticated: false,
        error: null,
        isAuthLoading: false,
      });
    }
  },

  refreshToken: async () => {
    try {
      await authService.refreshToken();
      // After refresh, validate to get user data
      const { user } = await authService.validateToken();
      set({ user, isAuthenticated: true });
      return true;
    } catch {
      // If refresh fails, logout
      get().logout();
      return false;
    }
  },

  checkAuth: async () => {
    set({ isAuthLoading: true });
    try {
      const user = await authService.validateToken();
      set({ user, isAuthenticated: true, isAuthLoading: false });
      return true;
    } catch {
      // Try refresh token
      const refreshed = await get().refreshToken();
      if (refreshed) {
        set({ isAuthLoading: false });
        return true;
      } else {
        set({ user: null, isAuthenticated: false, isAuthLoading: false });
        return false;
      }
    }
  },

  initializeAuth: async () => {
    set({ isAuthLoading: true });
    await get().checkAuth();
  },

  clearError: () => set({ error: null }),

  // One-off actions with loading + messages
  register: async (userData) => {
    set({ registerLoading: true, registerMessage: null });
    try {
      const res = await authService.register(userData);
      set({ registerLoading: false, registerMessage: res.message || "Registration successful, Verify your email!" });
      return res;
    } catch (error) {
      set({ registerLoading: false, registerMessage: error.message });
      throw error;
    }
  },

  forgotPassword: async (email) => {
    set({ forgotPasswordLoading: true, forgotPasswordMessage: null });
    try {
      const res = await authService.forgotPassword(email);
      set({ forgotPasswordLoading: false, forgotPasswordMessage: res.message });
      return res;
    } catch (error) {
      set({ forgotPasswordLoading: false, forgotPasswordMessage: error.message });
      throw error;
    }
  },

  resetPassword: async (data) => {
    set({ resetPasswordLoading: true, resetPasswordMessage: null });
    try {
      const res = await authService.resetPassword(data);
      set({ resetPasswordLoading: false, resetPasswordMessage: res.message });
      return res;
    } catch (error) {
      set({ resetPasswordLoading: false, resetPasswordMessage: error.message });
      throw error;
    }
  },

  verifyEmail: async (token) => {
    set({ verifyEmailLoading: true, verifyEmailMessage: null });
    try {
      const res = await authService.verifyEmail(token);
      set({ verifyEmailLoading: false, verifyEmailMessage: res.message });
      return res;
    } catch (error) {
      set({ verifyEmailLoading: false, verifyEmailMessage: error.message });
      throw error;
    }
  },

  resendVerification: async (email) => {
    set({ resendVerificationLoading: true, resendVerificationMessage: null });
    try {
      const res = await authService.resendVerification(email);
      set({ resendVerificationLoading: false, resendVerificationMessage: res.message });
      return res;
    } catch (error) {
      set({ resendVerificationLoading: false, resendVerificationMessage: error.message });
      throw error;
    }
  },
}));
