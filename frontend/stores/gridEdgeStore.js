import { create } from "zustand";
import { gridEdgeService } from "../services/gridEdgeService";

export const useGridEdgeStore = create((set) => ({
  edge: null,
  loading: false,
  error: null,

  createEdge: async (gridId, edgeData) => {
    set({ loading: true, error: null });
    try {
      const edge = await gridEdgeService.createEdge(gridId, edgeData);
      set({ edge, loading: false });
      return edge;
    } catch (error) {
      set({ loading: false, error: error.message });
      throw error;
    }
  },

  getEdge: async (gridId, edgeId) => {
    set({ loading: true, error: null });
    try {
      const edge = await gridEdgeService.getEdge(gridId, edgeId);
      set({ edge, loading: false });
      return edge;
    } catch (error) {
      set({ loading: false, error: error.message });
      throw error;
    }
  },

  updateEdge: async (gridId, edgeId, edgeData) => {
    set({ loading: true, error: null });
    try {
      const edge = await gridEdgeService.updateEdge(gridId, edgeId, edgeData);
      set({ edge, loading: false });
      return edge;
    } catch (error) {
      set({ loading: false, error: error.message });
      throw error;
    }
  },

  updateEdgeState: async (gridId, edgeId, stateData) => {
    set({ loading: true, error: null });
    try {
      const edge = await gridEdgeService.updateEdgeState(
        gridId,
        edgeId,
        stateData
      );
      set({ edge, loading: false });
      return edge;
    } catch (error) {
      set({ loading: false, error: error.message });
      throw error;
    }
  },

  deleteEdge: async (gridId, edgeId) => {
    set({ loading: true, error: null });
    try {
      const res = await gridEdgeService.deleteEdge(gridId, edgeId);
      set({ edge: null, loading: false });
      return res;
    } catch (error) {
      set({ loading: false, error: error.message });
      throw error;
    }
  },

  clearEdge: () => set({ edge: null, error: null }),
}));
