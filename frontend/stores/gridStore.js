import { create } from "zustand";
import { gridService } from "../services/gridService";

export const useGridStore = create((set) => ({
  // State
  grids: [],
  currentGrid: null,
  error: null,

  // Loading states
  listLoading: false,
  detailLoading: false,
  createLoading: false,
  updateLoading: false,
  deleteLoading: false,

  // Actions
  fetchGridsForWorkspace: async (workspaceId) => {
    set({ listLoading: true, error: null });
    try {
      const grids = await gridService.listGridsForWorkspace(workspaceId);
      set({ grids, listLoading: false });
      return grids;
    } catch (error) {
      set({ listLoading: false, error: error.message });
      throw error;
    }
  },

  fetchGridById: async (gridId) => {
    set({ detailLoading: true, error: null });
    try {
      const grid = await gridService.getGridById(gridId);
      set({ currentGrid: grid, detailLoading: false });
      return grid;
    } catch (error) {
      set({ detailLoading: false, error: error.message });
      throw error;
    }
  },

  createGrid: async (workspaceId, payload) => {
    set({ createLoading: true, error: null });
    try {
      const grid = await gridService.createGrid(workspaceId, payload);
      set((state) => ({
        grids: [...state.grids, grid],
        createLoading: false,
      }));
      return grid;
    } catch (error) {
      set({ createLoading: false, error: error.message });
      throw error;
    }
  },

  updateGrid: async (gridId, payload) => {
    set({ updateLoading: true, error: null });
    try {
      const updated = await gridService.updateGrid(gridId, payload);
      set((state) => ({
        grids: state.grids.map((g) =>
          g.id === gridId ? updated : g
        ),
        currentGrid:
          state.currentGrid?.id === gridId
            ? updated
            : state.currentGrid,
        updateLoading: false,
      }));
      return updated;
    } catch (error) {
      set({ updateLoading: false, error: error.message });
      throw error;
    }
  },

  deleteGrid: async (gridId) => {
    set({ deleteLoading: true, error: null });
    try {
      await gridService.deleteGrid(gridId);
      set((state) => ({
        grids: state.grids.filter((g) => g.id !== gridId),
        currentGrid:
          state.currentGrid?.id === gridId
            ? null
            : state.currentGrid,
        deleteLoading: false,
      }));
    } catch (error) {
      set({ deleteLoading: false, error: error.message });
      throw error;
    }
  },

  clearGridError: () => set({ error: null }),

  resetCurrentGrid: () => set({ currentGrid: null }),
}));
