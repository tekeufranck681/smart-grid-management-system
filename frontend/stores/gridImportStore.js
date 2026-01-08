import { create } from "zustand";
import { gridImportService } from "../services/gridImportService";

export const useGridImportStore = create((set) => ({
  importedGrid: null,
  importLoading: false,
  error: null,

  importGridFromFile: async (workspaceId, file) => {
    set({ importLoading: true, error: null });
    try {
      const grid = await gridImportService.importGridFromFile(workspaceId, file);
      set({ importedGrid: grid, importLoading: false });
      return grid;
    } catch (error) {
      set({ importLoading: false, error: error.message });
      throw error;
    }
  },

  clearImport: () => set({ importedGrid: null, error: null }),
}));
