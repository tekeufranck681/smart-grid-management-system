import { create } from "zustand";
import { workspaceService } from "../services/workspaceService";

export const useWorkspaceStore = create((set) => ({
  // State
  workspaces: [],
  currentWorkspace: null,
  error: null,

  // Loading states
  listLoading: false,
  detailLoading: false,
  createLoading: false,
  updateLoading: false,
  deleteLoading: false,

  // Actions
  fetchWorkspaces: async () => {
    set({ listLoading: true, error: null });
    try {
      const workspaces = await workspaceService.listWorkspaces();
      set({ workspaces, listLoading: false });
      return workspaces;
    } catch (error) {
      set({ listLoading: false, error: error.message });
      throw error;
    }
  },

  fetchWorkspaceById: async (workspaceId) => {
    set({ detailLoading: true, error: null });
    try {
      const workspace = await workspaceService.getWorkspaceById(workspaceId);
      set({ currentWorkspace: workspace, detailLoading: false });
      return workspace;
    } catch (error) {
      set({ detailLoading: false, error: error.message });
      throw error;
    }
  },

  createWorkspace: async (payload) => {
    set({ createLoading: true, error: null });
    try {
      const workspace = await workspaceService.createWorkspace(payload);
      set((state) => ({
        workspaces: [...state.workspaces, workspace],
        createLoading: false,
      }));
      return workspace;
    } catch (error) {
      set({ createLoading: false, error: error.message });
      throw error;
    }
  },

  updateWorkspace: async (workspaceId, payload) => {
    set({ updateLoading: true, error: null });
    try {
      const updated = await workspaceService.updateWorkspace(
        workspaceId,
        payload
      );
      set((state) => ({
        workspaces: state.workspaces.map((w) =>
          w.id === workspaceId ? updated : w
        ),
        currentWorkspace:
          state.currentWorkspace?.id === workspaceId
            ? updated
            : state.currentWorkspace,
        updateLoading: false,
      }));
      return updated;
    } catch (error) {
      set({ updateLoading: false, error: error.message });
      throw error;
    }
  },

  deleteWorkspace: async (workspaceId) => {
    set({ deleteLoading: true, error: null });
    try {
      await workspaceService.deleteWorkspace(workspaceId);
      set((state) => ({
        workspaces: state.workspaces.filter((w) => w.id !== workspaceId),
        currentWorkspace:
          state.currentWorkspace?.id === workspaceId
            ? null
            : state.currentWorkspace,
        deleteLoading: false,
      }));
    } catch (error) {
      set({ deleteLoading: false, error: error.message });
      throw error;
    }
  },

  clearWorkspaceError: () => set({ error: null }),

  resetCurrentWorkspace: () => set({ currentWorkspace: null }),
}));
